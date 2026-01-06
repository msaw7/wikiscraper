from setuptools import setup, find_packages 

setup(
    name="wiki_tools",
    version="0.1.0",
    author="Mateusz Sawicki",
    description="Package for scraping wikis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "numpy",
        "wordfreq",
        "tabulate",
        "regex",
        "matplotlib",
        "lxml",
        "html5lib"
    ],
)
