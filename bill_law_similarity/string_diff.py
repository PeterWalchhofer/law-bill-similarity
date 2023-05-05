import re

import swalign
from diff_match_patch import diff_match_patch
from IPython.display import HTML

dmp = diff_match_patch()
dmp.Diff_Timeout = 0


def diff(a, b):
    diff = dmp.diff_main(a, b)
    return diff


def show_diffs(a=None, b=None, diff=None, timeout=0):
    assert (a and b) or diff
    dmp = diff_match_patch()
    dmp.Diff_Timeout = timeout

    diff = diff or dmp.diff_main(a, b)
    # dmp.diff_cleanupMerge(diff)
    html = dmp.diff_prettyHtml(diff)
    html = re.sub("background:#e6ffe6", "color:#337a33", html)  # green
    html = re.sub("background:#ffe6e6", "color:#913c3c", html)  # red
    levenshtein = dmp.diff_levenshtein(diff)
    p_style = "p style='margin:0'"
    html = (
        f"<{p_style}>Levenshtein distance: {levenshtein}</p>"
        + f"<{p_style}>Similarity: {100-levenshtein*100/max(len(a),len(b)):.2f}%</p>"
        + f"<{p_style}>Length: {len(a)} vs {len(b)} (diff: {(len(b)-len(a))*100/len(b):.2f}%)</p>"
        + "<hr/>"
        + html
    )
    return HTML(html)


def sw_align(text_a, text_b):
    match = 2
    mismatch = -1
    beginning_gap_penalty = -5
    gap_extension_penalty = -0.5

    scoring = swalign.NucleotideScoringMatrix(match, mismatch)

    sw = swalign.LocalAlignment(
        scoring,
        gap_penalty=beginning_gap_penalty,
        gap_extension_penalty=gap_extension_penalty,
    )  # you can also choose gap penalties, etc...
    alignment = sw.align(text_a, text_b)
    return alignment.identity
