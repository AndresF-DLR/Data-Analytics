# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:40:15 2018

@author: riosa
"""

#To Do:
#Use tags at the bottom of main page as categories? Figure out how to collect them as well as the URL_Categories
#Maybe create a separate function (or include into simple_get()) for creating the BeautifulSoup HTML content?

#Data Viz. / Study Ideas: 
# 1. Mentions per Author (Bar Chart); 2. Books' # Tags and # Section (Bivariate Point Chart); 3. Mentions per Book (Bar Chart)
#Most "overarching" books - which books show up in a wide range of categories?
#After getting the books + titles, obtain content from articles themselves - word frequencies per category?
#After everything, maybe create a natural language procesing recommender?

"""
Observations:
    - At first, "The Ghost Map: The Story of London's Most Terrifying Epidemic" appeared to be the most "ovearching" book - the articles it was featured in
    cover the most ground  in terms of categories. BUT it was not featured in that many articles to begin with. 
    - No books seems to belong to more than 7 categories while having more than 2 articles (closest one is The Ghost Map, with two articles and that reach 8 categories)
    - Then cames "On Liberty" - it is featured in 9 different articles, but many appear to be in Philosophy (it only shows up in a total of 4 categories)
    - Finally, there is "Nineteen Eighty-Four: a book featured in 8 Articles that stretch throughout 7 categories
    
"""


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re

URL = "https://fivebooks.com/category/"

#This is for the not-so-automatic scrape...
URL_categories = ["philosophy-books","history", "fiction", "politics-and-society", "mathematics-and-science", "economics-business-and-investing", \
                "art-design-and-architecture", "best-kids-books", "world-and-travel", "mind-psychology", "health-and-lifestyle", "nature-and-environment", \
                "technology", "food-and-cooking", "literary-nonfiction-and-biography", "music-and-drama", "religion", "sports-games-and-hobbies"]

#URL_categories = ["philosophy-books", "history"]

def simple_get(url):
    """
    Attempts to get the content at 'url' by making an HTTP GET request
    If content-type of response is some kind of HTML/XML, return the text content, otherwise return NONE
    """
    
    try:
        #closing() ensures that any network resources are freed when they go out of scope in the with block
        #Helps prevent fatal error and network timeouts
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error("Error during requests to {0} : {1}".format(url, str(e)))
        return None
    
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise
    """
    content_type = resp.headers["Content-Type"].lower()
    return(resp.status_code == 200
           and content_type is not None
           and content_type.find('html') > -1)
    

def log_error(e):
    """
    Prints errors
    """
    print(e)
    
def collect(bs_html, D, category):
    
    page_sections = bs_html.find_all("article", class_ = "infinite-item archive-interview")
        
    titles = []
    
    subjects = []
    
    title_subject_counter = -1
    
    for section in page_sections:
        
        section_title = section.find("h2").get_text()
        
        section_subject = section.find("span", class_ = "subject").get_text()
        
        titles.append(section_title)
        
        subjects.append(section_subject)
    
    page_books = bs_html.find_all("li", class_ = (["single-book small-20-6 columns ", "single-book small-4 columns "]))    
    
    for book in page_books:
        
        book_position = int(book.get('data-position'))
        
        if book_position == 0:
            title_subject_counter += 1
            
        book_title_and_author = book.find("h2").get_text()
        book_title_and_author = book_title_and_author.split("\n")
        
        book_title = book_title_and_author[0].strip()
        
        book_author = book_title_and_author[1].strip()
        book_author = book_author[3:]
        
        if ("," or "&") in book_author and ("translated and abridged") not in book_author:
            book_author = re.split(', | &', book_author)
        
#            book_author = book_author.split(",")
#            print(book_author)
            
#        elif "&" in book_author:
#            book_author = book_author.split("&")
        
        book_article, book_subject = titles[title_subject_counter], subjects[title_subject_counter]
        
        if book_title in D:
#            D[book_title]["Subject"].append(book_subject)
#            D[book_title]["Article(s)"].append(book_article)
#            
            #Controls for books in articles that have been tagged as multiple categories
            if category not in D[book_title]["Category"]:
                D[book_title]["Category"].append(category)
                
            if book_subject not in D[book_title]["Subject"]:
                D[book_title]["Subject"].append(book_subject)
                
            if book_article not in D[book_title]["Article(s)"]:
                D[book_title]["Article(s)"].append(book_article)
            
        else:
            D[book_title] = {"Author(s)": [], "Subject": [book_subject], "Article(s)": [book_article], "Category": [category]}
            
            if type(book_author) == list:
                for author in book_author:
                    if author not in ["None", "and"]:
                        D[book_title]["Author(s)"].append(author)
                
            else:
                D[book_title]["Author(s)"].append(book_author)
            
    try:
        #Check if the parser must collect information from a subsequent page in the category
        next_page_html = bs_html.find("a", class_ = "infinite-more-link").get("href")
        print("Going into " + next_page_html)
        return next_page_html
    
    except AttributeError:
        #At the last page of the category, the parser found no link to a subsequent page
        print("Done with Category - " + category)
        return None
    

def FiveBooksParser(D):
    
    for category in URL_categories:
        print("Begin " + URL + category)
        raw_html = simple_get(URL + category)
        
        html = BeautifulSoup(raw_html, 'html.parser')
        
        counter = collect(html, D, category)
        
        while counter is not None:
            #Continue parsing through web-pages until the counter no longer represents the link to a subsequent page in the category
            raw_html = simple_get(counter)
            
            html = BeautifulSoup(raw_html, 'html.parser')
        
            counter = collect(html, D, category)
            
if __name__ == '__main__':
    
    book_dictionary = {}
    
    FiveBooksParser(book_dictionary)
                    
        
        
        
        
        