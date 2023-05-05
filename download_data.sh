#!/bin/bash

# Define array of country-data_url pairs
declare -A country_data_urls=(
  ["austria"]="www.dropbox.com/sh/ro217tj7wfmvc3x/AADlBnRrEs-TtMp4tOskpYG-a/Austria?dl=1"
  ["germany"]="www.dropbox.com/sh/ro217tj7wfmvc3x/AADzcNa5rW3O0tfKA1VeG6g1a/Germany?dl=1"
 )

# Iterate through the array
for country in "${!country_data_urls[@]}"; do
  data_url=${country_data_urls[$country]}
  
  # Create directory for data
  mkdir -p "data/${country}"
  
  # Download data from URL and save as zip file
  wget -O "data/${country}/${country}.zip" "${data_url}"
  
  # Unzip data to new directory with the same name as the country
  unzip "data/${country}/${country}.zip" -d "data/${country}"

  # Fix encoding of the corpus
  Rscript fixEncoding.R "data/${country}/Corpus_speeches_${country}.RDS"
  
  # Remove the zip file
  rm "data/${country}/${country}.zip"
done
