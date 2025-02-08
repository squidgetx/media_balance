# make extract_all file="input_data.tsv" dest="destination_dir"
extract_all:
	mkdir -p $(dest);
	mkdir -p tmp;
	python3 journalist_extractor.py $(file) tmp/1.tsv;
	Rscript process_journalists.R tmp/1.tsv tmp/2.tsv;
	read -p "Manually review partial matches and errors. Press enter to continue...";
	python3 get_metadata.py tmp/2.tsv tmp/3.tsv
