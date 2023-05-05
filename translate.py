from transformers import pipeline
import polars as pl


def load_df(type):
    df = pl.read_csv(f"data/annotated/{type}_sub_sec_pairs.csv").rename(
        {"sec_a_text": "bill_text", "sec_b_text": "law_text"}
    )
    return df


def translate_series(series):
    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de", max_length=460, device=0)
    result_list = pipe(series.to_list(), **{'truncation':True,'max_length':460})
    return pl.Series([result["translation_text"] for result in result_list])


def translate(df): 
    return df.fill_null("").select([
        pl.col("sec_a_id"),
        pl.col("sec_b_id"),
        pl.col("sec_a_title").map(lambda x: translate_series(x)),
        pl.col("sec_b_title").map(lambda x: translate_series(x)),
        pl.col("bill_text").map(lambda x: translate_series(x)),
        pl.col("law_text").map(lambda x: translate_series(x)),
        pl.col("label"),
    ])

train = load_df("train")
val = load_df("val")
test = load_df("test")

train_de = translate(train)
val_de = translate(val)
test_de = translate(test)

train_de.write_csv("data/annotated/train_sub_sec_pairs_de.csv")
val_de.write_csv("data/annotated/val_sub_sec_pairs_de.csv")
test_de.write_csv("data/annotated/test_sub_sec_pairs_de.csv")