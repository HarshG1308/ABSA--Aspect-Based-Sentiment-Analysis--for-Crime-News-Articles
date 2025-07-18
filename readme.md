# News Crime ABSA Project

## Overview

This project scrapes recent crime-related news articles from The Times of India and The Hindu, then uses aspect-based sentiment analysis (ABSA) to determine sentiment towards individuals mentioned in these articles.

---

## Features

- Scrapes news articles published within the last 48 hours from two Indian sources
- Identifies articles on crimes such as fraud, murder, and scams
- Extracts metadata: title, content, date/time, URL, named persons, and age (if available)
- Cleans and tokenizes the article text
- Detects sentences mentioning individuals
- Utilizes a pre-trained transformer model for ABSA to assess sentiment (positive, negative, or neutral) towards each individual in the articles
- Outputs negative profiles (individuals discussed negatively) in CSV and JSON formats
- Modular and well-commented scripts for ease of understanding

---

## Setup Instructions

1. **Clone this Repository:**

   ```bash
   git clone https://github.com/<your-username>/news-absa-project.git
   cd news-absa-project
   ```

2. **Install Dependencies:**

   It's recommended to perform this in a new virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Run the Pipeline:**

   ```bash
   python main.py
   ```

4. **View Outputs:**

   All output files (scraped_articles_*.csv, negative_profiles_*.csv, detailed_results_*.json) will be located in the `outputs` folder.

---

## Notes

- The project utilizes a free HuggingFace ABSA model and spaCy for NLP tasks.
- Output columns in the negative profiles file include: name, age, article_url, article_title, article_date.
- If a person's age isn’t detected, the age field remains empty.
- To add more sources or keywords, edit `scraper.py`.

---

## Limitations and Improvements

- The project only checks a limited set of example article URLs by default (not the entire websites).
- Article structure may change, potentially breaking some data extraction if the website layout is updated.
- Sentiment analysis is contingent on the quality of the ABSA model.
- Can be extended to a full crawler (currently only samples URLs) if required.