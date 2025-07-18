import re
from nltk.tokenize import sent_tokenize

AGE_PATTERNS = [
    r'(\d{1,3})\s*(?:years?\s*old|yr|yrs)',
    r'age\s*(\d{1,3})',
    r'aged\s*(\d{1,3})',
    r'(\d{1,3})\s*-\s*year\s*-\s*old',
    r'\((\d{1,3})\)',
]

def clean_text(txt):
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = re.sub(r'\s+', ' ', txt)
    patterns = [
        r'Advertisement', r'Subscribe to.*?Newsletter', r'Follow us on.*?Twitter',
        r'Like us on.*?Facebook', r'Share.*?WhatsApp', r'Download.*?app',
        r'Copyright.*?\d{4}', r'All rights reserved', r'Terms.*?Conditions', r'Privacy.*?Policy'
    ]
    for pat in patterns:
        txt = re.sub(pat, '', txt, flags=re.IGNORECASE)
    return txt.strip()

def break_into_sentences(text):
    return [s.strip() for s in sent_tokenize(text) if s.strip()]

def extract_entities_spacy(text, nlp):
    data = {'persons': [], 'ages': []}
    if not nlp:
        return data
    parsed = nlp(text)
    for ent in parsed.ents:
        if ent.label_ == "PERSON":
            nm = ent.text.strip()
            if len(nm) > 2 and nm not in data['persons']:
                data['persons'].append(nm)
    for pat in AGE_PATTERNS:
        found = re.findall(pat, text, re.IGNORECASE)
        for x in found:
            try:
                num = int(x)
                if 1 <= num <= 120 and num not in data['ages']:
                    data['ages'].append(num)
            except Exception:
                continue
    return data

def analyze_person_sentiment(full_txt, person, pipe):
    if not pipe:
        return {"sentiment": "neutral", "confidence": 0.0}
    inp = f"{full_txt} [SEP] {person}"
    result = pipe(inp)
    if result and isinstance(result, list) and result:
        pred = result[0]
        label = pred['label'].lower()
        conf = pred['score']
        if "positive" in label or "pos" in label:
            sent = "positive"
        elif "negative" in label or "neg" in label:
            sent = "negative"
        else:
            sent = "neutral"
        return {"sentiment": sent, "confidence": conf, "raw_label": pred['label']}
    return {"sentiment": "neutral", "confidence": 0.0}
