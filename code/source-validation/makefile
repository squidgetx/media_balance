validate250:
	./fetch_annotations.sh
	python check_potato.py
	python construct_potato_tsv.py

anno250:
	python extract-sources-v3.py ../../data/climate-excerpts/climate.250.tsv
	python dedup-sources.py ../../data/climate-excerpts/sources.gpt.250.json
	python ../annotation/make_anno_file.py ../../data/climate-excerpts/sources.gpt.250.json ../annotation/climate_sources/data_files/out250.json
	git add -f ../annotation/climate_sources/data_files/out250.json


