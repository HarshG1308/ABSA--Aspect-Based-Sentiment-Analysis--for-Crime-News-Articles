import nltk
import os
import pandas as pd
import json
from datetime import datetime   

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import spacy

from scraper import get_articles
from text_processing import clean_text, break_into_sentences, extract_entities_spacy, analyze_person_sentiment


nltk.data.find('tokenizers/punkt')
def main():
    print(">>> Running scraping ABSA pipeline >>>")
    articles = get_articles()

    print("loading transformer and spaCy models")
    model_name = "yangheng/deberta-v3-base-absa-v1.1"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    absa_model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    absapipe = pipeline("text-classification", model=absa_model, tokenizer=tokenizer)
    nlp = spacy.load("en_core_web_sm") 
    
    processed = []
    all_profiles = []
    negative_profiles = []
    for art in articles:
        clean_cont = clean_text(art['content'])
        sents = break_into_sentences(clean_cont)
        person_sents = []
        for sent in sents:
            ents = extract_entities_spacy(sent, nlp)
            if ents['persons']:
                person_sents.append({'sentence': sent, 'persons': ents['persons'], 'ages': ents['ages']})
        all_ents = extract_entities_spacy(f"{art['title']}. {clean_cont}", nlp)
        processed.append({
            "title": art['title'],
            "content": clean_cont,
            "url": art['url'],
            "publication_date": art['publication_date'],
            "source": art['source'],
            "sentences": sents,
            "person_sentences": person_sents,
            "entities": all_ents,
        })

    # ABSA sentiment
    for doc in processed:
        txt = f"{doc['title']}. {doc['content']}"
        for person in doc['entities']['persons']:
            age = None
            for d in doc['person_sentences']:
                if person in d['persons'] and d['ages']:
                    age = d['ages'][0]
                    break
            sentiment_result = analyze_person_sentiment(txt, person, absapipe)
            profile = {
                "name": person,
                "age": age,
                "article_url": doc['url'],
                "article_title": doc['title'],
                "article_publication_date": doc['publication_date'],
                "sentiment": sentiment_result["sentiment"],
                "confidence": round(sentiment_result.get("confidence", 0.0), 3),
                "source": doc['source']
            }
            all_profiles.append(profile)
            if profile["sentiment"] == "negative":
                negative_profiles.append(profile)

    # Save output
    time_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    pd.DataFrame(articles).to_csv(os.path.join(output_dir, f"scraped_articles_{time_now}.csv"), index=False)
    pd.DataFrame(negative_profiles).to_csv(os.path.join(output_dir, f"negative_profiles_{time_now}.csv"), index=False)

    result = {
        "scraped_articles": articles,
        "all_profiles": all_profiles,
        "negative_profiles": negative_profiles,
        "statistics": {
            "total_articles_scraped": len(articles),
            "total_profiles": len(all_profiles),
            "negative_profiles": len(negative_profiles),
            "sources": list(set(a['source'] for a in articles))
        }
    }
    with open(os.path.join(output_dir, f"detailed_results_{time_now}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    stats = result["statistics"]
    print("\n--- SUMMARY ---")
    print(f"Articles scraped: {stats['total_articles_scraped']}")
    print(f"Total profiles analyzed: {stats['total_profiles']}")
    print(f"Negative profiles: {stats['negative_profiles']}")
    print(f"Sources: {', '.join(stats['sources'])}")

if __name__ == "__main__":
    main()
    