import os
import pandas as pd
import requests
from bs4 import BeautifulSoup


def explore_website():
    # Define the URL
    url = "https://pauljarley.wordpress.com/"
    
    # Make the request
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code == 200:
        print("Successfully connected to the website!")
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Print the title of the page
        print("\n1. Page Title:")
        print(soup.title.text if soup.title else "No title found")
        
        # 2. Find all article elements
        articles = soup.find_all('article')
        print(f"\n2. Number of articles found: {len(articles)}")
        
        # 3. Look at the first article's structure in detail
        if articles:
            first_article = articles[0]
            print("\n3. Structure of the first article:")
            print(first_article.prettify())
            
            # 4. Examine available classes in the first article
            print("\n4. Classes found in the first article:")
            for element in first_article.find_all(class_=True):
                print(f"Tag: {element.name}, Class: {element['class']}")
        
        # 5. Find all unique HTML tags used
        all_tags = soup.find_all(True)
        unique_tags = set(tag.name for tag in all_tags)
        print("\n5. All unique HTML tags used on the page:")
        print(sorted(unique_tags))
        
    else:
        print(f"Failed to connect. Status code: {response.status_code}")


import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

def scrape_deans_blog():
    base_url = "https://pauljarley.wordpress.com/"
    response = requests.get(base_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    posts = soup.find_all('article')
    print(f"Found {len(posts)} articles")
    
    data = []
    
    for post in posts:
        try:
            title_element = post.find('h1', class_='entry-title')
            if title_element:
                title = title_element.find('a').text.strip()
                url = title_element.find('a')['href']
                print(f"\nProcessing article: {title}")
                print(f"URL: {url}")
            else:
                continue
                
            date_element = post.find('time', class_='entry-date')
            date = date_element.text.strip() if date_element else "Date not found"
            
            post_response = requests.get(url)
            post_soup = BeautifulSoup(post_response.content, 'html.parser')
            
            content_element = post_soup.find('div', class_='entry-content')
            post_text = content_element.get_text(strip=True) if content_element else "Content not found"
            
            # Use OrderedDict to track unique comments
            comments = OrderedDict()
            comments_section = post_soup.find('ol', id='commentlist') or post_soup.find('ol', class_='commentlist')
            
            if comments_section:
                print(f"Found comments section for: {title}")
                # Use a more specific selector to avoid nested duplicates
                comment_items = comments_section.find_all('article', class_='comment', recursive=False)
                if not comment_items:  # Fallback to li if no articles found
                    comment_items = comments_section.find_all('li', class_='comment', recursive=False)
                
                for comment in comment_items:
                    author_element = (comment.find('cite', class_='fn') or 
                                    comment.find('span', class_='fn') or 
                                    comment.find('b', class_='fn'))
                    
                    comment_text_element = (comment.find('div', class_='comment-content') or 
                                          comment.find('div', class_='comment-text'))
                    
                    if author_element and comment_text_element:
                        author = author_element.text.strip()
                        comment_text = comment_text_element.get_text(strip=True)
                        
                        # Create a unique key for each comment
                        comment_key = f"{author}:{comment_text}"
                        if comment_key not in comments:
                            print(f"Found comment by: {author}")
                            comments[comment_key] = {
                                'author': author,
                                'comment': comment_text
                            }
            
            # Add to data list with deduplicated comments
            data.append({
                'title': title,
                'date': date,
                'url': url,
                'post_text': post_text,
                'comments': list(comments.values())
            })
            
        except Exception as e:
            print(f"Error processing post: {str(e)}")
            continue
    
    if data:
        output_folder = '/Users/zhaoxin/Desktop/2025 spring/aaron/repository/MAN7916/assignments/submissions/assignment_2'
        output_file = os.path.join(output_folder, 'dean_scraping.csv')
        
        rows = []
        for entry in data:
            if entry['comments']:
                for comment in entry['comments']:
                    rows.append({
                        'Post Title': entry['title'],
                        'Post Date': entry['date'],
                        'Post URL': entry['url'],
                        'Post Text': entry['post_text'],
                        'Comment Author': comment['author'],
                        'Comment Text': comment['comment']
                    })
            else:
                rows.append({
                    'Post Title': entry['title'],
                    'Post Date': entry['date'],
                    'Post URL': entry['url'],
                    'Post Text': entry['post_text'],
                    'Comment Author': '',
                    'Comment Text': ''
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nData saved to {output_file}")
        print(f"Total posts processed: {len(data)}")
        total_comments = sum(len(entry['comments']) for entry in data)
        print(f"Total comments captured: {total_comments}")
    else:
        print("No data found to save")

if __name__ == "__main__":
    scrape_deans_blog()