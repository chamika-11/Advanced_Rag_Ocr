import re
import spacy
import pytesseract
import cv2

nlp=spacy.load("en_core_web_sm")

def extract_refex(text):
    data={}
    #regex patterns
    date_pattern = r"\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b"
    amount_pattern = r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?"
    # id_pattern = r"\b[0-9]{6,12}\b"

    dates=re.findall(date_pattern,text)
    amounts=re.findall(amount_pattern,text)
    # ids=re.findall(id_pattern,text)

    if dates:data["dates"]=dates
    if amounts:data["amounts"]=amounts
    # if ids:data["possible_ids"]=ids

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
    

def extract_kv_from_image(image_path,keywords=None):
    if keywords is None:
        keywords=["name","account","date","loan","amount","NIC"]

    image=cv2.imread(image_path)
    data=pytesseract.image_to_data(image,output_type=pytesseract.Output.DICT)

    extracted={}

    for i in range(len(data['text'])):
        word=data['text'][i].strip().lower()
        if word in keywords:
            x,y,w,h=data['left'][i],data['top'][i],data['width'][i],data['height'][i]
            try:
                next_word=data['text'][i+1].strip()
                if next_word:
                    extracted[word]=next_word
            except IndexError:
                continue

    return extracted
    


def extract_structured_data(text, image_path=None):
    regex_data = extract_refex(text)
    ner_data = extract_with_ner(text)
    kv_data = {}

    if image_path:
        kv_data = extract_kv_from_image(image_path)

    structured = {**regex_data, **ner_data, **kv_data}
    return structured