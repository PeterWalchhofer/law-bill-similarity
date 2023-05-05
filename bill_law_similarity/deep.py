import torch
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("distiluse-base-multilingual-cased-v1")


def bert_cosine(bill_sents, law_sents):
    bill_emb = model.encode(bill_sents, convert_to_tensor=True)
    law_emb = model.encode(law_sents, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(bill_emb, law_emb)
    return cosine_scores.to("cpu")


def bert_align(bill_sents, law_sents, verbose=False):
    cosine_scores = bert_cosine(bill_sents, law_sents)
    align = cosine_scores.clone()
    alignment = []
    for i in range(min(cosine_scores.shape)):
        sim_max = align.max()
        max_idx = (align == sim_max).nonzero()[0]
        alignment.append((max_idx, sim_max.item()))
        align[max_idx[0], :] = -1  # set rows to 0
        align[:, max_idx[1]] = -1  # set cols to 0
        cosine_scores[max_idx[0], max_idx[1]] = -1

    avg = sum([x[1] for x in alignment]) / len(alignment)

    if verbose:
        print(
            f"bill_len: {len(bill_sents)}\n law_len: {len(law_sents)}\n avg without p: {avg}"
        )
    if len(bill_sents) == len(law_sents):
        return avg

    # Penalize if not the same amount of sentences in bill and laws
    if len(bill_sents) > len(law_sents):
        agg_dim = 1
        weight_sents = bill_sents
    else:
        agg_dim = 0
        weight_sents = law_sents

    # determine which sentence has no match
    idx_leftover = torch.where(~(cosine_scores == -1).any(dim=agg_dim))[0]
    lengths = [len(x) for x in weight_sents]
    penalties = 0
    for i in idx_leftover:
        length_leftover = len(weight_sents[i])
        penalties += length_leftover / sum(lengths)

    return avg - penalties


def bert_avg_pool(bill_sents, law_sents):
    bill_emb = model.encode(bill_sents, convert_to_tensor=True).mean(dim=0)
    law_emb = model.encode(law_sents, convert_to_tensor=True).mean(dim=0)
    cosine_scores = util.pytorch_cos_sim(bill_emb, law_emb)[0]
    return cosine_scores.to("cpu").item()

def bert_max_avg(bill_sents, law_sents):
    bill_emb = model.encode(bill_sents, convert_to_tensor=True)
    law_emb = model.encode(law_sents, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(bill_emb, law_emb)
    max_bill, _ = cosine_scores.max(dim=1)
    sim_bill = max_bill.mean() / max_bill.shape[0]
    max_law, _ = cosine_scores.max(dim=0)
    sim_law = max_law.mean() / max_law.shape[0]
    score = max(sim_bill, sim_law)
    return score.to("cpu").item()