import re
import spacy

nlp=spacy.load("en_core_web_sm")

def extract_refex(text):
    data={}
    #regex patterns
    date_pattern = r"\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b"
    amount_pattern = r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?"
    id_pattern = r"\b[A-Z0-9]{6,12}\b"

    dates=re.findall(date_pattern,text)
    amounts=re.findall(amount_pattern,text)
    ids=re.findall(id_pattern,text)

    if dates:data["dates"]=dates
    if amounts:data["amounts"]=amounts
    if ids:data["possible_ids"]=ids

    return data


def extract_with_ner(text):
    doc=nlp(text)
    data={"names":[],"organizations":[],"locations":[]}
    for ent in doc.ents:
        if ent.label_=="PERSON":
            data["names"].append(ent.text)
        elif ent.label_=="ORG":
            data["organizations"].append(ent.text)
        elif ent.label_=="GPE":
            data["locations"].append(ent.text)
        return data
    


def extract_structured_data(text):
    regex_data=extract_refex(text)
    ner_data=extract_with_ner(text)


    structured={**regex_data,**ner_data}
    return structured