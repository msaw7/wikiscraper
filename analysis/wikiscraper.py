import sys
from wikitools import Archive, Scraper
import argparse
from tabulate import tabulate
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

_WIKI_PREFIX = "https://bulbapedia.bulbagarden.net"
_WIKI_IDENTIFIER = "/wiki/"
_WIKI_LANG = "en"
_TERMINATION_KEYWORD = "There is currently no text in this page."
_START_MARKER = "<!-- start content -->"
_END_MARKER = "<!-- end content -->"
_DICT_PATH = "./word-counts.json"


def parse_and_validate_phrase(phrase: str) -> Scraper | None:
    phrase = phrase.replace(" ", "_")
    scraper = Scraper(f"{_WIKI_PREFIX}{_WIKI_IDENTIFIER}{phrase}")
    if not scraper.validate_source(_TERMINATION_KEYWORD):
        print("Page not found")
        return None
    return scraper


def summary(phrase: str):
    scraper = parse_and_validate_phrase(phrase)
    if not scraper:
        return

    paragraph = scraper.get_summary()
    print(paragraph)


def table(phrase: str, number: int, first_row_is_header: bool = False):
    scraper = parse_and_validate_phrase(phrase)
    if not scraper:
        return
    result = scraper.get_table(number - 1, first_row_is_header)
    if result is None:
        return

    print(result[0])
    for val, key in result[1]:
        print(f"{key} : {val}")
    result[0].to_csv(f"./{phrase}.csv")


def count_words(phrase: str):
    phrase = phrase.replace(" ", "_")
    archive = Archive(
        _WIKI_PREFIX,
        _WIKI_IDENTIFIER,
        _WIKI_LANG,
        _START_MARKER,
        _END_MARKER,
        Path(_DICT_PATH),
    )
    archive.count_words(phrase)


def analyze_relative_word_frequency(mode: str, count: int, chart: str):
    archive = Archive(
        _WIKI_PREFIX,
        _WIKI_IDENTIFIER,
        _WIKI_LANG,
        _START_MARKER,
        _END_MARKER,
        Path(_DICT_PATH),
    )
    table = archive.analyze_relative_word_frequency(mode, count)
    table = table.rename(columns={"occ_wiki": "Bulbapedia", "occ_lang": "English"})
    print(table)
    if chart is None:
        return

    zipf_table = table
    zipf_table["Bulbapedia"] = np.log10(zipf_table["Bulbapedia"]) + 9
    zipf_table["English"] = np.log10(zipf_table["English"]) + 9

    ax = zipf_table.plot(kind="bar")
    ax.set_title("Comparison of Bulbapedia and English word occurences in Zipf scale.")

    fig = ax.get_figure()
    fig.tight_layout()

    fig.savefig(chart, dpi=300, bbox_inches="tight")


def auto_count_words(phrase: str, depth: int, wait: float):
    phrase = phrase.replace(" ", "_")
    archive = Archive(
        _WIKI_PREFIX,
        _WIKI_IDENTIFIER,
        _WIKI_LANG,
        _START_MARKER,
        _END_MARKER,
        Path(_DICT_PATH),
    )
    archive.auto_count_words(phrase, depth, wait, {""})


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple scraper for Bulbapedia")

    parser.add_argument("-s", "--summary", type=str, help="Extract first paragraph")

    parser.add_argument("-t", "--table", type=str, help="Export table to CSV")
    parser.add_argument("-n", "--number", type=int)
    parser.add_argument("-frih", "--first-row-is-header", action="store_true")

    parser.add_argument("-cw", "--count-words", type=str, help="Log word counts (JSON)")

    parser.add_argument(
        "-arwf",
        "--analyze-relative-word-frequency",
        action="store_true",
        help="Compare frequencies and plot",
    )
    parser.add_argument("-m", "--mode", type=str)
    parser.add_argument("-c", "--count", type=int)
    parser.add_argument("-ch", "--chart", type=str)

    parser.add_argument(
        "-acw", "--auto-count-words", type=str, help="Recursive crawling and counting"
    )
    parser.add_argument("-d", "--depth", type=int)
    parser.add_argument("-w", "--wait", type=float)

    args = parser.parse_args()

    instruction_count = 0
    instructions = [
        "summary",
        "table",
        "count_words",
        "analyze_relative_word_frequency",
        "auto_count_words",
    ]
    for ins in instructions:
        if getattr(args, ins, None):
            instruction_count += 1

    if instruction_count != 1:
        print("Invalid number of instructions")
        return 1

    print(
        "Output below was generated using an article originally published on https://bulbapedia.bulbagarden.net/wiki.\nIt is licensed under BY-NC-SA.\n"
    )

    if args.summary:
        summary(args.summary)

    if args.table:
        if args.number is None:
            print("Invalid table number")
            return 1
        table(args.table, args.number, args.first_row_is_header)

    if args.count_words:
        count_words(args.count_words)

    if args.analyze_relative_word_frequency:
        if args.mode is None or args.mode not in ["article", "language"]:
            print("Invalid mode")
            return 1
        if args.count is None:
            print("Invalid count")
            return 1

        analyze_relative_word_frequency(args.mode, args.count, args.chart)

    if args.auto_count_words:
        if args.depth is None or args.depth < 0:
            print("Invalid depth")
            return 1
        if args.wait is None or args.wait < 0:
            print("Invalid wait time")
            return 1

        auto_count_words(args.auto_count_words, args.depth, args.wait)

    return 0


if __name__ == "__main__":
    sys.exit(main())
