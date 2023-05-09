import string

import polars as pl
import spacy
from polars import col
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import paired_cosine_distances
from tqdm import tqdm

lang_model_mapping = {
    "de": "de_core_news_sm",
    "en": "en_core_web_sm",
}


def load_nlp(lang):
    nlp = spacy.load(
        lang_model_mapping[lang],
        disable=[
            "ner",
        ],
    )
    nlp.max_length = 100000000
    return nlp


def tokenize(text_column, lang, process_bar_position=0):
    nlp = load_nlp(lang)
    docs = nlp.pipe(text_column)
    doc_tokens = []
    for doc in tqdm(docs, total=len(text_column), position=process_bar_position):
        parsed_doc = {
            "tokens": [token.text.lower() for token in doc],
            "lemmas": [token.lemma_.lower() for token in doc],
            "tags": [token.tag_ for token in doc],
            "sents": [sent.text for sent in doc.sents],
        }
        doc_tokens.append(parsed_doc)

    return pl.Series(doc_tokens)


def fit_vectorize(df, ngram_range=(1, 1), lemmatize=False):
    cv = TfidfVectorizer(
        norm="l2",
        token_pattern=None,
        lowercase=False,
        tokenizer=lambda x: x,
        ngram_range=ngram_range,
    )
    cv.fit(df["bill_tokens" if not lemmatize else "bill_lemmas"])
    cv.fit(df["law_tokens" if not lemmatize else "law_lemmas"])
    return cv


def vectorize(text_column, cv):
    token_matrix = cv.transform(text_column)
    return token_matrix


def compute_distances(law_vectors, bill_vectors):
    return 1 - paired_cosine_distances(law_vectors, bill_vectors)


def preprocess(data, lang):
    data_tokenized = (
        data.with_columns(
            [
                col("bill_text")
                .map(lambda x: tokenize(x, lang=lang))
                .alias("bill_text_tokens"),
                col("law_text")
                .map(lambda x: tokenize(x, lang=lang, process_bar_position=1))
                .alias("law_text_tokens"),
            ]
        )
        # dict to series
        .with_columns(
            [
                col("bill_text_tokens").struct.field("tokens").alias("bill_tokens"),
                col("bill_text_tokens").struct.field("lemmas").alias("bill_lemmas"),
                col("bill_text_tokens").struct.field("tags").alias("bill_tags"),
                col("bill_text_tokens").struct.field("sents").alias("bill_sents"),
                col("law_text_tokens").struct.field("tokens").alias("law_tokens"),
                col("law_text_tokens").struct.field("lemmas").alias("law_lemmas"),
                col("law_text_tokens").struct.field("tags").alias("law_tags"),
                col("law_text_tokens").struct.field("sents").alias("law_sents"),
            ]
        ).drop(["bill_text_tokens", "law_text_tokens"])
    )
    return data_tokenized


def compute_cosine_similarity(data_tokenized, ngram_range=(1, 1), lemmatize=False):
    cv = fit_vectorize(data_tokenized, ngram_range=ngram_range)
    bill_vectors = vectorize(
        data_tokenized["bill_tokens" if not lemmatize else "bill_lemmas"], cv
    )
    law_vectors = vectorize(
        data_tokenized["law_tokens" if not lemmatize else "law_lemmas"], cv
    )
    distances = compute_distances(law_vectors, bill_vectors)
    return distances
