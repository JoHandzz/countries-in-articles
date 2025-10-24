---
editor_options: 
  markdown: 
    wrap: 72
---

# countries-in-articles

## Multi-Source News Scraper & Country Analyzer

This project is an automated data pipeline that scrapes daily news
articles from multiple international media outlets (BBC, DR, ARD). It
stores the articles in a SQLite database, uses Natural Language
Processing (NLP) to identify all countries mentioned in the text, and
provides R scripts for final data analysis and filtering.

## Features

Multi-Source & Multilingual: Scrapes articles from BBC (English), DR
(Danish), and ARD (German).

Automated Scraping: Designed to be run on a daily schedule (e.g., using
GitHub Actions).

NLP Country Analysis: Uses spaCy and custom demonym lookup maps to
accurately find countries mentioned in each article.

Data Processing: Using R tidyverse

## How it Works: The Data Pipeline

The project operates in three main stages:

### Stage 1: Scraping (Python)

Python scripts (e.g., scrape_bbc.py, scrape_dr.py) run, fetching article
headlines, URLs, and full article text.

New articles are saved as rows in the articles table in database.db.

### Stage 2: NLP Analysis (Python)

The main analyze.py script is run.

The script updates the article's row, filling the countries column and
setting processed = 1.

### Stage 3: Data Analysis (R)

An R script (analyze.R) reads the final, processed data from the
database (or a CSV export).

It uses dplyr to filter, clean, and balance the dataset (e.g., removing
sports, ensuring equal article counts per media per day).

The final, clean dataset is then ready for analysis or visualization.

## Tech Stack

Python3

requests & BeautifulSoup4: For web scraping.

sqlite3: For database storage.

spacy: For Natural Language Processing (NER).

R

dplyr & readr: For data manipulation and analysis.

Automation (Recommended)

GitHub Actions or a local cron job.

## Setup and Installation

Set up Python Environment:

Download spaCy Models: You must download the language models for the
analysis to work.

python -m spacy download en_core_web_sm python -m spacy download
de_core_news_sm python -m spacy download da_core_news_sm

Set up R Environment: Open an R session and install the required
packages

Create the Database: The Python scripts will create database.db if it
doesn't exist, but you must create the articles table first. You can do
this using the SQLite command-line tool. See jupityr notebook.
