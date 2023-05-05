#!/bin/bash
mkdir -p data/annotated
for VAR in test_sub_sec_pairs.csv train_sub_sec_pairs.csv val_sub_sec_pairs.csv
do
  wget -O data/annotated/"$VAR" https://github.com/hikoseon12/learning-bill-similarity/raw/main/data/subsection_pairs/human_annotated_pairs/"$VAR"
done
