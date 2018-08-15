# -*- coding: utf-8 -*-
"""
Updated on Tue Aug 14 16:08:22 2018

@author: AndresF-DLR
"""

#To Do:
#Use tags at the bottom of main page/side of each section as sub-topics? Figure out how to collect them as well as the URL_Categories
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

#URL_categories = ["history"]

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
 
    """
    Page Subtopics Scraper
    #check if page has sub-topics - typically only the first page of each section has them
    page_subtopics = bs_html.find("div", class_ = "related_topics")
    
    if page_subtopics:
        suptopics = []
        
        page_subtopics = page_subtopics.find_all("a")
        
        for subtopic in page_subtopics:
            a = subtopic.get_text()
            subtopics.append(a)
            
        print(page_subtopics)
        
    """
    
    #Divide page into each article's entry/row 
    page_sections = bs_html.find_all("article", class_ = "infinite-item archive-interview")
    
    #Initialize repository to store each article's title, subject and referrer
    article_titles = []
    subjects = []
    referrers = []
    
    #Initialize counter that will assign the appropiate title, subject, and referrer to each article's books
    title_subject_counter = -1
    
    #Obtain list of all article entries/sections in a single webpage
    for section in page_sections:
        
        #Article Titles
        section_title = section.find("h2").get_text()
        article_titles.append(section_title)
        
        #Article Subjects
        section_subject = section.find("span", class_ = "subject").get_text()
        subjects.append(section_subject)
        
        #Article Referrers (Obtained from the title)
        dissected_title = section_title.split()
        
        #Referrer Format Option 1 - Referrer's name is in the article's title after the word "by" 
        if "by" in dissected_title: 
           i = dissected_title.index("by")
           
           #Referrer function obtains all components of title after "by"-element index
           referrer = lambda x: x[i + 1:]
           
           #Join referrer's components (usually First Name, Last Name) as a string
           section_referrer = " ".join(referrer(dissected_title))
        
        #Referrer Format Option 2 - Referrer's name is at the beginning of the article's title.
        #Check if the first two components of the title are a First Name and a Last Name               
        elif dissected_title[1][0].isupper() or dissected_title[2][0].isupper():
            section_referrer = dissected_title[:2]
            
            #In case of two-part Last Names with a lowercase component - e.g. Joseph van Deer
            if dissected_title[2][0].isupper():
                section_referrer = dissected_title[:3]
                
            section_referrer = " ".join(section_referrer)
            
        #Referrer Format Option 3 - Outlier article title case with an uncommon format (PENDING)
        else:
            section_referrer = "N/A"
        
        referrers.append(section_referrer)
            
    #Obtain list of each article's books
    page_books = bs_html.find_all("li", class_ = (["single-book small-20-6 columns ", "single-book small-4 columns "]))    
    
    #Loop through each article's books to obtain author, title, and create dictionary entry
    for book in page_books:
        
        #Data-position keeps track of which books belong in which articles
        book_position = int(book.get('data-position'))
        
        #A position of 0 means the book belongs to the next article entry with different title, subject, and referrer
        if book_position == 0:
            title_subject_counter += 1
        
        #Book title and author are drawn from the same website division, divided by a \n character
        book_title_and_author = book.find("h2").get_text()
        book_title_and_author = book_title_and_author.split("\n")
        
        #Isolate book title
        book_title = book_title_and_author[0].strip()
        
        #Isolate book author(s) taking into account "by " characters
        book_author = book_title_and_author[1].strip()
        book_author = book_author[3:]
        
        #Check if book has multiple authors by looking for " , " or "&" characters
        #Ignores names in entries with "translated and abridged" author description format (PENDING)
        if ("," or "&") in book_author and ("translated and abridged") not in book_author:
            book_author = re.split(', | &', book_author)
        
        #Matches the book with it's respective article information (title, subject and referrer) through the counter updated by the data position
        book_article, book_subject, book_referrer = article_titles[title_subject_counter], subjects[title_subject_counter], referrers[title_subject_counter]
        
        #If book has multiple mentions/is already in the dictionary thanks to another article, only append the new article's information
        if book_title in D:
            
            #Controls for books in articles that have been tagged as multiple categories
            if category not in D[book_title]["Category"]:
                D[book_title]["Category"].append(category)
                
            if book_subject not in D[book_title]["Subject"]:
                D[book_title]["Subject"].append(book_subject)
                
            if book_article not in D[book_title]["Article(s)"]:
                D[book_title]["Article(s)"].append(book_article)
                
            if book_referrer not in D[book_title]["Referrer(s)"]:
                D[book_title]["Referrer(s)"].append(book_referrer)
            
        #Append each books's whole entry into dictionary the first time it is mentioned    
        else:
            D[book_title] = {"Author(s)": [], "Subject": [book_subject], "Article(s)": [book_article], "Category": [category], "Referrer(s)": [book_referrer]}
            
            """
            if category == "reader-lists":
                D[book_title]["Reader Pick"]: True
            """
            
            #For books with multiple authors: remove filler words and store each name independently
            if type(book_author) == list:
                for author in book_author:
                    if author not in ["None", "and"]:
                        D[book_title]["Author(s)"].append(author)
                        
            #For books with single authors: append the name to the book's dictionary entry  
            else:
                D[book_title]["Author(s)"].append(book_author)
    
    
    #Check if the parser must collect information from a subsequent page in the category       
    try:
        next_page_html = bs_html.find("a", class_ = "infinite-more-link").get("href")
        print("Going into " + next_page_html)
        return next_page_html

    #At the last page of the category, the parser found no link to a subsequent page
    except AttributeError:
        print("Done with Category - " + category)
        return None
    

def FiveBooksParser(D):
    
    #Loop through website's pre-defined categories (PENDING Automatization)
    for category in URL_categories:
        print("Begin " + URL + category)
        raw_html = simple_get(URL + category)
        html = BeautifulSoup(raw_html, 'html.parser')
        
        counter = collect(html, D, category)
        
        #Continue parsing through web-pages until the counter no longer represents a functional link to the next page in the category
        while counter is not None:
            raw_html = simple_get(counter)
            
            html = BeautifulSoup(raw_html, 'html.parser')
        
            counter = collect(html, D, category)
            
if __name__ == '__main__':
    
    book_dictionary = {}
    
    FiveBooksParser(book_dictionary)
