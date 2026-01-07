import sys
from wikitools import Scraper


def main() -> int:
    with open("./bulbapedia_page.html", "r") as file:
        source = file.read()
    try:
        scraper = Scraper(source, True)
        summary = scraper.get_summary().rstrip()
        beginning = "Ash Ketchum (Japanese:"
        assert beginning == summary[: len(beginning)]
        end = "Pokdddémon Journeys."
        assert end == summary[-len(end) :]
    except:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
