import jaro
import polars as pl
from bow import bow_overlap, bow_pos_overlap
from deep import bert_align, bert_avg_pool, bert_cosine, bert_max_avg
from docu_toads import docu_toads_similarity
from polars import col
from string_diff import diff, sw_align
from vector import compute_cosine_similarity, preprocess


def load_df(type, lang="de"):
    df = pl.read_csv(f"data/annotated/{type}_sub_sec_pairs.csv").rename(
        {"sec_a_text": "bill_text", "sec_b_text": "law_text"}
    )
    preprocessed = preprocess(df, lang)
    return preprocessed


def comparison_wrapper(col_a, col_b, func, name):
    return (
        pl.struct([pl.col(col_a), pl.col(col_b)])
        .apply(lambda x_dict: func(x_dict[col_a], x_dict[col_b]))
        .alias(name)
    )


def pos_bow_ol_wrapper(col_a, col_b, col_a_tags, col_b_tags, func, name):
    return (
        pl.struct(
            [pl.col(col_a), pl.col(col_b), pl.col(col_a_tags), pl.col(col_b_tags)]
        )
        .apply(
            lambda x_dict: func(
                x_dict[col_a], x_dict[col_b], x_dict[col_a_tags], x_dict[col_b_tags]
            )
        )
        .alias(name)
    )


def comparison_wrapper(col_a, col_b, func, name):
    return (
        pl.struct([pl.col(col_a), pl.col(col_b)])
        .apply(lambda x_dict: func(x_dict[col_a], x_dict[col_b]))
        .alias(name)
    )


def pos_bow_ol_wrapper(col_a, col_b, col_a_tags, col_b_tags, func, name):
    return (
        pl.struct(
            [pl.col(col_a), pl.col(col_b), pl.col(col_a_tags), pl.col(col_b_tags)]
        )
        .apply(
            lambda x_dict: func(
                x_dict[col_a], x_dict[col_a_tags], x_dict[col_b], x_dict[col_b_tags]
            )
        )
        .alias(name)
    )


def similarity_metrics(df):
    # # Polars paralellizes with_columns(). For some reason, it crashes with BERT -> workaround
    df_deep = df.with_columns(
        [comparison_wrapper("bill_sents", "law_sents", bert_align, "bert_aligned")]
    )
    df_deep = df_deep.with_columns(
        [comparison_wrapper("bill_sents", "law_sents", bert_avg_pool, "bert_avg_pool")]
    )
    df_deep = df_deep.with_columns(
        [comparison_wrapper("bill_sents", "law_sents", bert_max_avg, "bert_max_avg")]
    )
    df_deep = df_deep.with_columns(
        [comparison_wrapper("bill_sents", "law_sents", bert_cosine, "bert_full")]
    )

    tfidf_cos_sim = compute_cosine_similarity(df)
    tfidf_cos_sim_bigram = compute_cosine_similarity(df, (2, 2))
    tfidf_cos_sim_lemma = compute_cosine_similarity(df)
    tfidf_cos_sim_bigram_lemma = compute_cosine_similarity(df, (2, 2))

    return df_deep.clone().select(
        [
            # TF_IDF Cos-Sim
            pl.Series(tfidf_cos_sim).alias("tfidf_cos_sim"),
            pl.Series(tfidf_cos_sim_bigram).alias("tfidf_cos_sim_bigram"),
            pl.Series(tfidf_cos_sim_lemma).alias("tfidf_cos_sim_lemma"),
            pl.Series(tfidf_cos_sim_bigram_lemma).alias("tfidf_cos_sim_bigram_lemma"),
            # SW Align
            comparison_wrapper("bill_text", "law_text", sw_align, "sw_align"),
            # DocuToads
            comparison_wrapper(
                "bill_tokens", "law_tokens", docu_toads_similarity, "docu_toads"
            ),
            comparison_wrapper(
                "bill_lemmas", "law_lemmas", docu_toads_similarity, "docu_toads_lemma"
            ),
            # BOW Overlap
            comparison_wrapper("bill_tokens", "law_tokens", bow_overlap, "bow_ol"),
            comparison_wrapper(
                "bill_tokens",
                "law_tokens",
                lambda a, b: bow_overlap(a, b, 2),
                "bow_ol_bigrams",
            ),
            comparison_wrapper(
                "bill_lemmas", "law_lemmas", bow_overlap, "bow_ol_lemma"
            ),
            comparison_wrapper(
                "bill_lemmas",
                "law_lemmas",
                lambda a, b: bow_overlap(a, b, 2),
                "bow_ol_bigrams_lemma",
            ),
            # POS BOW Overlap
            pos_bow_ol_wrapper(
                "bill_tokens",
                "law_tokens",
                "bill_tags",
                "law_tags",
                bow_pos_overlap,
                "pos_bow_ol",
            ),
            pos_bow_ol_wrapper(
                "bill_tokens",
                "law_tokens",
                "bill_tags",
                "law_tags",
                lambda a, b, c, d: bow_pos_overlap(a, b, c, d, 2),
                "pos_bow_bigrams",
            ),
            pos_bow_ol_wrapper(
                "bill_lemmas",
                "law_lemmas",
                "bill_tags",
                "law_tags",
                bow_pos_overlap,
                "pos_bow_ol_lemma",
            ),
            pos_bow_ol_wrapper(
                "bill_lemmas",
                "law_lemmas",
                "bill_tags",
                "law_tags",
                lambda a, b, c, d: bow_pos_overlap(a, b, c, d, 2),
                "pos_bow_bigrams_lemma",
            ),
            # Jaro Winkler
            comparison_wrapper(
                "bill_text", "law_text", jaro.jaro_winkler_metric, "jaro_winkler"
            ),
        ]
    )


# train = load_df("train")
val = load_df("val").sample(10)
# test = load_df("test")

val_metrics = similarity_metrics(val)
# train_metrics = similarity_metrics(train)
# test_metrics = similarity_metrics(test)

if __name__ == "__main__":
    val_metrics.write_csv("train_metrics_de.csv")
