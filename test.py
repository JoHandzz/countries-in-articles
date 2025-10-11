from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import sqlite3
import re 


def get_tagesschau_article_body_fixed(full_link):
    """
    Fetches and extracts the main text body from a Tagesschau article URL, 
    excluding the related article teasers.
    """
    print(f"Fetching article body from: {full_link}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(full_link, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch article {full_link}: {e}")
        return ""

    soup = BeautifulSoup(response.text, 'lxml')

    # 1. Target the main article container (<article> tag)
    # The main text content is within the <article> tag which is a child of 
    # <div class="layout-content">. This isolates it from the sidebars/footers.
    main_article = soup.find('article', class_='container content-wrapper__group')
    
    if not main_article:
        print("Could not find the main article container.")
        return ""
        
    # 2. Define the specific class used for main content paragraphs
    # These classes position the text in the main column and appear consistently
    # on the article body paragraphs.
    main_text_classes = [
        'textabsatz columns twelve m-ten m-offset-one l-eight l-offset-two',
        'textabsatz m-ten m-offset-one l-eight l-offset-two columns twelve'
    ]
    
    # 3. Find all main text paragraphs only within the main article container
    # This prevents scraping paragraphs from the teaser sections below.
    text_blocks = main_article.find_all('p', class_=main_text_classes)

    cleaned_text_blocks = []
    
    # 4. Extract and clean text
    for p_tag in text_blocks:
        text = p_tag.get_text().strip()
        
        # Filter out very short or empty elements that might be lingering, 
        # but keep the main text
        if text and len(text) > 20: 
            # Remove the non-breaking space used for formatting lists/headings (like ' ')
            text = text.replace(u'\xa0', u' ').strip()
            
            # The first paragraph often starts with bolded lead text, ensure it's captured
            cleaned_text_blocks.append(text)
            
    # 5. Join the cleaned blocks into a single body string
    article_body = " ".join(cleaned_text_blocks)
    
    # Optional final cleanup for redundant spaces
    article_body = re.sub(r'\s+', ' ', article_body).strip()

    return article_body

# --- Test the function with your example URL ---
full_link = 'https://www.tagesschau.de/ausland/amerika/trump-gesundheit-106.html'

article_body = get_tagesschau_article_body_fixed(full_link)

print("\n--- Extracted Article Body ---")
# print(article_body)

# Print a formatted version to confirm all text is there and teasers are gone
print(article_body)
