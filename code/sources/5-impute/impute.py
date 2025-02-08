# Step 1: Install required packages

# pip install sentence-transformers pandas scikit-learn

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# Example dataset
data = pd.read_csv('orgs.dime.tsv', sep='\t')

# Step 2: Text embeddings with SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # Or any sentence transformer model
#data['text_embeddings'] = data['cluster.desc'].apply(lambda x: model.encode(x))
X = model.encode(data['cluster.desc'])
#X = pd.DataFrame(list(data['text_embeddings'])) 
y = data['cfscore']


# Step 6: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


def eval(model, name):
    model.fit(X_train, y_train)
    # Step 8: Make predictions
    y_pred = model.predict(X_test)
    # Step 9: Evaluate the model (R-squared)
    r2_score = model.score(X_test, y_test)
    mse = np.mean(np.power(y_pred - y_test, 2))
    print(f"{name} R-squared score: {r2_score:.4f}, MSE {mse:.4f}")

eval(LinearRegression(), "linear")
eval(RidgeCV(), "Ridge")
eval(LassoCV(), "Lasso")
