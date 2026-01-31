import pytest
from wikitools import Scraper


def test_get_summary(generic_html):
    scraper = Scraper(generic_html, True)
    assert (
        scraper.get_summary()
        == "This is a bold paragraph with italic text, underlined text, and a link."
    )


def test_get_table(generic_html, bulbapedia_html):
    scraper = Scraper(generic_html, True)
    assert scraper.get_table(-1, False) is None
    assert scraper.get_table(0, False) is not None
    assert scraper.get_table(1, False) is not None
    assert scraper.get_table(2, False) is None

    scraper2 = Scraper(bulbapedia_html, True)
    # Look for table with fields 'Voice actor' and 'Language'
    found_actors_table = False
    for i in range(0, 100):
        table = scraper2.get_table(i, True)
        if table is not None:
            if "Voice actor" in table[0].columns:
                found_actors_table = True
                assert "Language" in table[0].columns
                print(table[0])
    assert found_actors_table


def test_count_words(hidden_content_html):
    scraper = Scraper(hidden_content_html, True)
    words = scraper.count_words("<!-- START -->", "<!-- END -->")
    assert words is not None

    # Elements of HTML should not be included
    assert "foo" not in words

    # Elements outside of content should not be included
    assert "bar" not in words
    assert "abc" not in words
    
    # Words should be converted to lowercase
    assert "hide" in words
    assert "HIDE" not in words
