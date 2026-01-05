from io import StringIO
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
from tabulate import tabulate
import csv
import regex as re

class Scraper:

    def __init__(self, source: str, use_local: bool=False):
        self.page : BeautifulSoup
        if(use_local):
            self.page = BeautifulSoup(source, 'html.parser')
        else:
            response = requests.get(source)
            self.page = BeautifulSoup(response.text, 'html.parser')
            
    def validate_source(self, termination_keyword: str) -> bool:
        if(termination_keyword in self.get_summary()):
            return False
        return True

    def get_summary(self) -> str:
        paragraph = self.page.find('p')
        if(paragraph is None):
            return ''
        paragraph = paragraph.get_text()
        return paragraph
    
    def get_table(self, n: int, first_row_is_header: bool=False) -> tuple[pd.DataFrame, list] | None:
        table = self.page.find_all('table')
        if(n >= len(table) or n < 0):
            print('Table of given index not found')
            return None
        table = table[n]

        try:
            if(first_row_is_header):
                table = pd.read_html(StringIO(str(table)), header=0)[0]
            else:
                table = pd.read_html(StringIO(str(table)))[0]
        except:
            print('Error while parsing table')
            return None

        values: dict[str, int] = {}
        for content in list(table.stack()):
            if(content):
                keyword = str(content)
                values[keyword] = values.get(keyword, 0) + 1
        
        sorted_values = sorted(list(map(lambda t: t[::-1], values.items())), reverse=True)
        return (table, sorted_values)


    def count_words(self, start: str, end: str) -> dict[str, int]:
        # Take only the content out of the page
        raw_content = str(self.page)
        raw_content = raw_content[raw_content.find(start): raw_content.find(end)]

        # Remove HTML symbols from content
        text_content = BeautifulSoup(raw_content, 'html.parser').get_text()
        text_content = ''.join(list(map(lambda c: c.lower() if (c.isalpha() or c == ' ') else ' ', text_content)))

        # Create word dictionary
        counter: dict[str, int] = {}
        for word in text_content.split():
            counter[word] = counter.get(word, 0) + 1

        return counter
    
    def get_wiki_links(self, wiki_identifier: str) -> list[str]:
        links = self.page.find_all('a')
        wiki_links: list[str] = []
        for link in links:
            url = link.get('href')
            # Check if the url links inside the wiki
            if(url is not None and url[0:len(wiki_identifier)] == wiki_identifier): # short circuit
                wiki_links.append(url[len(wiki_identifier):])
        
        return wiki_links

