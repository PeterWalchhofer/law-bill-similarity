# Experiment
The experiment can be found in `experiment.ipynb`. Run the notebook in order to reproduce the experiments mentioned in the paper.
Do not forget to install to necessary requirements:
```
pip install -r requirements.txt
```

The output also is persisted in `data/results`.
The qualitative evaluation (the examples where there was lots of divergence between surface level methods and the fine-tuned BERT model) can be found at `data/qualitative_evaluation`
# Annotator
The annotater web app can be found in `/annotator`.
Install the dependnecies via
```
cd /annotator
npm install
```

To run the web app use
```
npm start dev
```

# ChatGPT prompts
The scripts to generate the prompts is found at `chat_gpt_prompts/gpt_prompter.py`. 
The output of the script is saved at `chat_gpt_prompts/prompts.txt`.
The results retrieved are saved at `chat_gpt_prompts/prompt_results.json`

# Translation of the dataset
The translated ground truth is saved along the original ground truth csvs at `data/annotated`. 
The script used to produce the CSVs is saved in project root at `translate.py`.