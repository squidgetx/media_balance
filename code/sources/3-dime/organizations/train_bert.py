from squidtools import util
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')
records = util.read_delim('matches_for_gpt_stg2.10k.combined.tsv')
textsim_data = util.read_delim('bert_training_textsim.pos.tsv')
textsim_data_neg = util.read_delim('bert_training_textsim.neg.tsv')

# Prepare training data
train_examples = [
    InputExample(
        texts=[row['name'], row['organization']], 
        label=1 if row['combined_gpt_label'] == 'TRUE' else 0
    ) for row in records
]
train_examples.extend([
    InputExample(
        texts=[row['name'], row['organization']], 
        label=1
    ) for row in textsim_data
])
train_examples.extend([
    InputExample(
        texts=[row['name'], row['organization']], 
        label=0
    ) for row in textsim_data_neg
]
)
print(f"training on {len(train_examples)} records")
# Create a DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Use contrastive loss for fine-tuning
train_loss = losses.CosineSimilarityLoss(model)

# Fine-tune the model
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1, warmup_steps=100)
model.save("fine_tuned_org_match_model.bert")


