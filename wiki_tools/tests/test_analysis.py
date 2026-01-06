from unittest.mock import patch, mock_open
from wiki_tools import Archive
from pathlib import Path

def test_analysis(bulbapedia_html):
    mock_content = '''{
  "pokémon": 2,
  "bulbazaur": 1,
  "the": 1
}'''
    _WIKI_PREFIX = 'https://bulbapedia.bulbagarden.net'
    _WIKI_IDENTIFIER = '/wiki/'
    _WIKI_LANG = 'en'
    _START_MARKER = '<!-- start content -->'
    _END_MARKER =  '<!-- end content -->'
    _DICT_PATH = './word-counts.json'


    archive = Archive(_WIKI_PREFIX, _WIKI_IDENTIFIER, _WIKI_LANG, _START_MARKER, _END_MARKER, Path(_DICT_PATH))
    with patch('wiki_tools.archive.open', mock_open(read_data=mock_content)):
        result = archive.analyze_relative_word_frequency('article', 3)
        assert('occ_wiki' in result.columns)
        assert('occ_lang' in result.columns)
        assert(result.at['pokémon', 'occ_wiki'] == 0.5)
        assert(result.at['bulbazaur', 'occ_wiki'] == 0.25)
        assert(result.at['the', 'occ_wiki'] == 0.25)
        val = result.at['bulbazaur', 'occ_lang']
        assert(val >= 0 and val <= 1)