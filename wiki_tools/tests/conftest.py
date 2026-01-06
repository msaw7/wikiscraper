import pytest
from pathlib import Path

@pytest.fixture
def generic_html():
    file_path = Path(__file__).parent / 'generic_page.html'
    with open(file_path, 'r') as file:
        return file.read()

@pytest.fixture
def bulbapedia_html():
    file_path = Path(__file__).parent / 'bulbapedia_page.html'
    with open(file_path, 'r') as file:
        return file.read()
    
@pytest.fixture
def hidden_content_html():
    file_path = Path(__file__).parent / 'hidden_content_page.html'
    with open(file_path, 'r') as file:
        return file.read()


