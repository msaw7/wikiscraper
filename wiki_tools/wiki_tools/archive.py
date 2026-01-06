import pandas as pd
from tabulate import tabulate
import json
from pathlib import Path
from .scraper import Scraper
import time
import wordfreq
import numpy as np

class Archive:

    def __init__(self, wiki_prefix: str, wiki_identifier: str, wiki_lang: str, start_marker: str, end_marker: str, dict_path: Path):
        self.wiki_prefix = wiki_prefix
        self.dict_path = dict_path
        self.prefix_length = len(wiki_prefix)
        self.wiki_identifier = wiki_identifier
        self.wiki_lang = wiki_lang
        self.start_marker = start_marker
        self.end_marker = end_marker


    def count_words(self, phrase: str, scrape_links: bool=False) -> None | list[str]:
        # Fetch dictionary file if present.
        global_dictionary = {}
        if(self.dict_path.is_file()):
            with open(self.dict_path, 'r') as file:
                global_dictionary = json.load(file)

        # Scrape the url with our phrase.
        source = f'{self.wiki_prefix}{self.wiki_identifier}{phrase}'
        scraper = Scraper(source)
        local_dictionary = scraper.count_words(self.start_marker, self.end_marker)

        # Write down the scraped values in dictionary file.
        for item in local_dictionary.items():
            global_dictionary[item[0]] = global_dictionary.get(item[0], 0) + item[1]
        with open(self.dict_path, 'w') as file:
            json.dump(global_dictionary, file)

        # Scrape all wiki links from the page if needed.
        if scrape_links:
            return scraper.get_wiki_links(self.wiki_identifier)

    def auto_count_words(self, phrase: str, depth: int, wait: float, visited: set[str]):
        # Prevent infinite recursion.
        if(phrase in visited):
            return
        visited.add(phrase)

        print(phrase)

        # Update the dictionary file and fetch links to wiki.
        wiki_links = self.count_words(phrase, scrape_links=True)
        if(wiki_links is None):
            print('Error')
            return

        # Wait to prevent sending too many requests.
        time.sleep(wait)

        # Recursively traverse phrase tree DFS-style.
        # Please note that this implementation only ensures that the depth of 
        # recursion is at most 'depth'. This means that the phrase tree can be
        # *significantly* smaller than a BFS-style search of same depth.
        # The size of the phrase tree is also dependent on the order which
        # links are visited.
        if(depth > 0):
            for link in wiki_links:
                self.auto_count_words(link, depth - 1, wait, visited) 

    def analyze_relative_word_frequency(self, mode: str, count: int) -> pd.DataFrame:
        # Fetch dictionary file if present.
        global_dictionary: dict[str, int] = {}
        if(self.dict_path.is_file()):
            with open(self.dict_path, 'r') as file:
                global_dictionary = json.load(file)

        wiki_occurences = pd.DataFrame.from_dict(global_dictionary, orient='index', columns=['occ_wiki'])
        total_wiki_occurences = sum(wiki_occurences['occ_wiki'])
        wiki_occurences['occ_wiki'] /= total_wiki_occurences
    
        if mode == 'article':
            wiki_occurences = wiki_occurences.sort_values(by=['occ_wiki'], ascending=False).head(count)
            # We do not use pandas merge to not fetch entire wordfreq dictionary.
            wiki_occurences['occ_lang'] = wiki_occurences.index.map(lambda e: wordfreq.word_frequency(e, self.wiki_lang))
            return wiki_occurences
        
        else: # mode == 'language'
            lang_most_common = wordfreq.top_n_list(self.wiki_lang, count, wordlist='best')
            lang_dict = {}
            for word in lang_most_common:
                lang_dict[word] = wordfreq.word_frequency(word, self.wiki_lang)
            lang_occurences = pd.DataFrame.from_dict(lang_dict, orient='index', columns=['occ_lang'])
            return lang_occurences.merge(wiki_occurences, how='left', left_index=True, right_index=True)
    

