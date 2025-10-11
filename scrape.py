from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import sqlite3
import re


def scrape_bbc(cursor, max_scrapes):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    """Scrapes the BBC homepage and saves articles to the database."""
    print("--- Starting BBC Scrape ---")
    date = datetime.today().strftime('%Y-%m-%d')
    url = 'https://www.bbc.com'
    base_url = 'https://www.bbc.com'


    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch BBC homepage: {e}")
        return

    soup = BeautifulSoup(response.text, 'lxml')
    headline_tags = soup.find_all('a', attrs={'data-testid': ['internal-link', 'external-anchor']})
    links = set()

    for n, link_tag in enumerate(headline_tags):
        if n > max_scrapes:
            break   # FOR TESTING, REMEMBER TO REMOVE


        headline_element = link_tag.find(['h2', 'h3'])
        headline = (headline_element.text.strip() if headline_element else link_tag.text.strip())

        raw_link = link_tag.get('href')
        if not raw_link:
            continue

        full_link = base_url + raw_link if raw_link.startswith('/') else raw_link

        if headline and len(headline) > 20 and full_link != base_url and full_link not in links:
            if 'British Broadcasting Corporation' in headline:   
                continue
            
            # Filter out unwanted links
            if any(keyword in full_link for keyword in ['/terms', '/contact', '/help', '/video', '/usingthebbc', '/cloud.email', '/account', '/audio']):
                continue

            links.add(full_link)
            
            is_nyhed = 1 if "/news" in full_link else 0
            
            if "/news" in full_link:
                type_nyhed = 'news'
            elif "/sport" in full_link:
                type_nyhed = 'sport'
            else:
                # A safer way to get the type without index errors
                url_segments = full_link.split("/")
                type_nyhed = url_segments[3] if len(url_segments) > 3 else 'other'

            try:
                article_response = requests.get(full_link, headers=headers, timeout=10)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'lxml')

                text_blocks = [p.text for p in article_soup.find_all('p')]
                text_body = " ".join(text_blocks)

                cursor.execute("""INSERT OR IGNORE INTO articles 
                    (headline, URL, date, is_nyhed, type_article, text_body, countries, KM_index, language, media, processed) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (headline, full_link, date, is_nyhed, type_nyhed, text_body, "", 0, "English", "BBC", 0))
                
                print(f"BBC: Added '{headline[:30]}...'")

            except requests.exceptions.RequestException as e:
                print(f"Could not fetch BBC article {full_link}: {e}")
            
            time.sleep(0.5)
    print("--- Finished BBC Scrape ---")


def scrape_dr(cursor, max_scrapes):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("--- Starting DR Scrape ---")
    date = datetime.today().strftime('%Y-%m-%d')
    
    def get_dr_body(hyperlink):
        try:
            response = requests.get(hyperlink, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            lines = soup.find_all('div', class_='dre-speech')
            return " ".join(i.text for i in lines)
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch DR article body from {hyperlink}: {e}")
            return ""

    try:
        response = requests.get('https://www.dr.dk', headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch DR homepage: {e}")
        return

    soup = BeautifulSoup(response.text, 'lxml')
    headers = soup.find_all('a', class_='hydra-card-title')

    for n, header in enumerate(headers):
        if n > max_scrapes:
                    break   # FOR TESTING, REMEMBER TO REMOVE

        title = header.text.strip()
        link = header.get('href')

        if not link or 'quiz' in link:
            continue

        hyperlink = link if link.startswith('http') else 'https://www.dr.dk' + link

        split_link = hyperlink.split('/')
        if len(split_link) > 3:
            if split_link[3] == 'nyheder':
                is_nyhed = 1
                type_nyhed = split_link[4] if len(split_link) > 4 else 'nyheder'
            else:
                is_nyhed = 0
                type_nyhed = split_link[3]
        else:
            is_nyhed = 0
            type_nyhed = 'other'

        text_body = get_dr_body(hyperlink)
        if text_body: # Only insert if we successfully got the body
            cursor.execute("""INSERT OR IGNORE INTO articles 
                        (headline, URL, date, is_nyhed, type_article, text_body, countries, KM_index, language, media, processed) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (title, hyperlink, date, is_nyhed, type_nyhed, text_body, "", 0, "Danish", "DR", 0))
            print(f"DR: Added '{title[:30]}...'")

        time.sleep(0.5)
    print("--- Finished DR Scrape ---")


def scrape_ARD(cursor, max_scrapes):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    """Scrapes the Tagesschau homepage and saves articles to the database."""
    print("--- Starting Tagesschau Scrape ---")
    date = datetime.today().strftime('%Y-%m-%d')
    url = 'https://www.tagesschau.de'
    base_url = 'https://www.tagesschau.de'

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch Tagesschau homepage: {e}")
        return

    soup = BeautifulSoup(response.text, 'lxml')
    # Target all 'a' tags that wrap a primary article (class='teaser__link')
    headline_tags = soup.find_all('a', class_='teaser__link')
    
    links = set()
    scraped_count = 0


    for link_tag in headline_tags:
        if scraped_count >= max_scrapes:
            break

        # 1. Extract Headline
        # Look for the span that holds the main headline text
        headline_element_main = link_tag.find('span', class_='teaser__headline')
        
        # Look for the optional 'topline' (e.g., section or subheading)
        headline_element_top = link_tag.find('span', class_='teaser__topline')

        headline = ""
        if headline_element_top and headline_element_main:
            # Combine top and main headline
            top_text = headline_element_top.text.strip()
            main_text = headline_element_main.text.strip()
            headline = f"{top_text}: {main_text}"
        elif headline_element_main:
            headline = headline_element_main.text.strip()
        else:
            continue

        # Clean up any residual HTML/text artifacts like the hyphenation spans
        headline = re.sub(r'\s*<span[^>]*>.*?</span>\s*', '', headline).strip()

    
        raw_link = link_tag.get('href')
        if not raw_link:
            continue
            
        full_link = base_url + raw_link if raw_link.startswith('/') else raw_link

        if headline and full_link != base_url and full_link not in links:
            if any(keyword in full_link for keyword in ['/kontakt', '/hilfe', '/video', '/audio', '/datenschutz', '/multimedia']):
                continue

            links.add(full_link)
            

            is_nyhed = 0
            type_nyhed = 'other'
            url_segments = full_link.split("/")

            if '/inland' in full_link or '/ausland' in full_link or "/wirtschaft" in full_link:
                is_nyhed = 1


            
            if len(url_segments) > 3:
                type_nyhed = url_segments[3].split('-')[0] if url_segments[3] else 'other'


            if "/sport" in full_link or "/fussball" in full_link:
                is_nyhed = 0 
                type_nyhed = 'sport'

            
           
            response1 = requests.get(full_link, headers=headers, timeout=10)
            soup1 = BeautifulSoup(response1.text, 'lxml')
            main_article = soup1.find('article', class_='container content-wrapper__group')
            
            if not main_article:
                return "SCRAPING FAILED"
                
            main_text_classes = ['textabsatz columns twelve m-ten m-offset-one l-eight l-offset-two','textabsatz m-ten m-offset-one l-eight l-offset-two columns twelve']
            text_blocks = main_article.find_all('p', class_=main_text_classes)
            cleaned_text_blocks = []
            
            for text in text_blocks:
                text = text.get_text().strip()
                if text and len(text) > 20: 
                    # Remove the non-breaking space used for formatting lists/headings (like ' ')
                    text = text.replace(u'\xa0', u' ').strip()
                    cleaned_text_blocks.append(text)
                    

            article_body = " ".join(cleaned_text_blocks)
            text_body = article_body


            try:
                # Assuming your database setup is correct
                cursor.execute("""INSERT OR IGNORE INTO articles 
                    (headline, URL, date, is_nyhed, type_article, text_body, countries, KM_index, language, media, processed) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (headline, full_link, date, is_nyhed, type_nyhed, text_body, "", 0, "German", "ARD", 0))
                
                print(f"Tagesschau: Added '{headline[:30]}...'")
                scraped_count += 1

            except Exception as e:
                print(f"Error saving to database: {e}")
            
            time.sleep(0.5) # Throttle the requests

    print(f"--- Finished Tagesschau Scrape (Added {scraped_count} articles) ---")

if __name__ == '__main__':
    MAX_SCRAPES = 100
   
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    
    scrape_bbc(c, MAX_SCRAPES)
    conn.commit() 

    scrape_dr(c, MAX_SCRAPES)
    conn.commit() 

    scrape_ARD(c, MAX_SCRAPES)


    conn.close()
    
    with open('logs.txt', 'a') as f:
        f.write("All scraping finished and database connection closed.\n")