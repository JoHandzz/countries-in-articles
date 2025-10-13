import requests
from bs4 import BeautifulSoup


full_link = "https://www.bbc.com/travel/article/20251009-sardinias-sacred-neolithic-fairy-houses"

# Assuming 'full_link' and 'headers' are defined
article_response = requests.get(full_link)
article_response.raise_for_status()
article_soup = BeautifulSoup(article_response.text, 'lxml')

# Find the main <article> tag first
main_article = article_soup.find('article')

text_body = ""
if main_article:
    # Now, find all <p> tags only within the <article> tag
    text_blocks = [p.get_text(strip=True) for p in main_article.find_all('p')]
    text_body = " ".join(text_blocks)
else:
    print("Warning: Could not find the <article> tag. Falling back to old method.")
    # Fallback to your original method if <article> isn't found
    text_blocks = [p.get_text(strip=True) for p in article_soup.find_all('p')]
    text_body = " ".join(text_blocks)


print(text_body)