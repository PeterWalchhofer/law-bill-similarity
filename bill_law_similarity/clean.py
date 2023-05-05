import re

rm_line_breaks = lambda x: x.replace("\r\n", " ")
rm_none_breaking_space = lambda x: x.replace("\xa0", " ")  # .replace("§\xa0", "§")
strip = lambda x: x.strip()
# exception for dates
rm_soft_hyphen = lambda x: x.replace("\xad", "")  # grenz\xadflächenaktive Substanzen

add_space_before_number = lambda x: re.sub(
    r"(?<![(\d\.,)/])(„?\(?\d+[a-z]?\)?)", r" \g<1>", x
)  # würde.(3) Ein Verfahren | Achtung„(3)“ | und2 Artikel wird folgendes Datum 20.03.19978
# exception for dates and lookahead for quote, e.g. "end of quote lalala."
add_space_after_dot = lambda x: re.sub(
    r"(\.(?!\d+)“?)", r"\g<1> ", x
)  # Stand der Wissenschaft.“2.Dem § 2 wird folgendes Datum 20.03.1997
add_space_after_punctuation = lambda x: re.sub(
    r"([,;:](?!\d+))", r"\g<1> ", x
)  # Stand der Wissenschaft.“2.Dem § 2 wird folgendes Datum 20.03.1997
add_space_after_quote = lambda x: re.sub(
    r"“(?![\)\.,;])", r"“ ", x
)  # except for "quote". and quote") Introduces: Arbeits(Einsatz)ort -> Arbeits(Einsatz) ort
add_space_after_brace = lambda x: re.sub(
    r"\)(?![“\.,;])", r") ", x
)  # except for "quote". and quote")
add_space_after_number_followed_by_capital = lambda x: re.sub(
    r"(\d+[a-z]?)([A-ZÄÖÜ][a-zäöüß]+)", r"\g<1> \g<2>", x
)  # Bund 2005Artikel 5Änderung des
# camel case to space
add_space_after_camel_case = lambda x: re.sub(
    r"([a-zäöüß]{2,})([A-ZÄÖÜ][a-zäöüß]+)", r"\g<1> \g<2>", x
)  # AufenthaltsgesetzesArtikel 6Änderung
add_space_before_symbol = lambda x: re.sub(r"([a-zäüö])(§)", "\g<1> \g<2>", x)

#  Europäischen Wirtschaftsraumsa) erschienen (§ 9) ist
# add_space_before_letter_enumaration = lambda x: re.sub(r"([a-zöäüß\s]+)([a-z]\))([a-zöäü\s])", r"\g<1> \g<2> \g<3>", x) # oderb)auf (neu)  hinausa) Arbeits(Einsatz)ort


rm_extra_spaces = lambda x: re.sub(r"\s+", " ", x)

remove_multiple_points = lambda x: re.sub(
    r"\.{4,}|(\.\s){4,}|(……){2,}", " ", x
)  #  befristeter Aufenthaltstitel (§ 8 Abs. 1 Z 1, 2 und 5 NAG)............ 20 Euro, bei Minderjährigen...................................................................................... 50 Euro b) unbefristeter Aufenthaltstitel (§ 8 Abs. 1 Z 3 und 4 NAG)............ 70 Euro, bei Minderjährigen.................................................................................... 100 Euro 2. von Amts wegen................................................................................... 100 Euro.“ b) Abs. 5a lautet: „(5a) Ausstellung 1. einer Anmeldebescheinigung (§ 9 Abs. 1 Z 1 NAG) oder einer Bescheinigung des Daueraufenthalts (§ 9 Abs. 2 Z 1 NAG)............................................................................................................ 15 Euro 2. einer Daueraufenthaltskarte (§ 9 Abs. 2 Z 2 NAG) oder einer Aufenthaltskarte für Angehörige eines EWR-Bürgers (§ 9 Abs. 1 Z 2


cleaning_pipeline_bill = [
    rm_line_breaks,
    rm_none_breaking_space,
    remove_multiple_points,
    rm_soft_hyphen,
    rm_extra_spaces,
    strip,
]
cleaning_pipeline_law = [
    rm_line_breaks,
    remove_multiple_points,
    rm_none_breaking_space,
    add_space_before_number,
    add_space_after_dot,
    add_space_after_punctuation,
    add_space_after_quote,
    add_space_after_brace,
    add_space_after_number_followed_by_capital,
    rm_soft_hyphen,
    add_space_after_camel_case,
    add_space_before_symbol,
    rm_extra_spaces,
    strip,
]


def clean_bill_aut(text):
    for f in cleaning_pipeline_bill:
        text = f(text)
    search = re.search(
        "Der Nationalrat hat beschlossen:|Der Nationalrat wolle beschließen:", text
    )
    if search is None:
        return None
    text = text[search.end() :]
    return text


def clean_law_aut(text):

    for f in cleaning_pipeline_law:
        text = f(text)
    search = re.search(
        "Der Nationalrat hat beschlossen:|Der Nationalrat wolle beschließen:", text
    )
    if search is None:
        return None
    text = text[search.end() :]
    return text


def clean_text_ger(text):
    search = re.search("Der Bundestag hat das folgende Gesetz beschlossen", text)
    if search is None:
        return None
    text = text[search.end() :]
    for f in [
        rm_line_breaks,
        rm_none_breaking_space,
        remove_multiple_points,
        rm_soft_hyphen,
        rm_extra_spaces,
        strip,
    ]:
        text = f(text)
    return text
