import playwright.sync_api as pw_s_api
import urllib.parse as urllib_p
import dotenv
import bs4

import envparse

dotenv.load_dotenv()
BOT_HANDLER_EMAIL = envparse.get_str("BOT_HANDLER_EMAIL")  # your email
BOT_HANDLER_URL = envparse.get_str(
    "BOT_HANDLER_URL"
)  # ideally docs such as my.page.com/bot
DEBUG_MODE = envparse.get_bool("DEBUG_MODE")
DEBUG_LOG_SIZE = envparse.get_int("DEBUG_LOG_SIZE")
if DEBUG_MODE:
    print("env vars:\n\t", BOT_HANDLER_EMAIL, DEBUG_MODE, DEBUG_LOG_SIZE)

# TODO add /bot to my website
# https://developers.whatismybrowser.com/learn/browser-detection/user-agents/user-agent-best-practices
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/User-Agent#examples
# https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests#use-automatic-solutions
USER_AGENT = (
    f"Mozilla/5.0 (compatible; BrawlBot/1.0.0; +{BOT_HANDLER_URL}; {BOT_HANDLER_EMAIL})"
)


def index_page(page: pw_s_api.Page, url: str) -> None:
    sub_pages = []

    try:
        # fetch the page content and wait for the network requests to stop
        # or for 5 seconds to pass
        page.goto(url, wait_until="networkidle", timeout=5000)
        # NOTE to self, if the above does not work or proves to
        # be error prone, try time.sleep(3) or something similar

        # get the html from the page then find and parse all the urls
        html = bs4.BeautifulSoup(page.content(), "html.parser")
        for link in html.find_all("a"):
            href = link.get("href")

            # if the href is empty or is not a str (class element can have several elements)
            # so link.get() is typed `str|list[str]|none` and we want only `str`
            if not isinstance(href, str):
                continue

            # resolve the relative paths then parse to inspect it
            absolute_url = urllib_p.urljoin(url, href)
            parsed_url = urllib_p.urlparse(absolute_url)

            # ensure url leads to a website (ignore mailto: or tel:)
            if parsed_url.scheme not in ["http", "https"]:
                continue

            # clean the url of any fragments (ex: '#')
            # https://docs.python.org/3/library/urllib.parse.html#url-parsing
            cleaned_url = parsed_url._replace(fragment="").geturl()

            sub_pages.append(cleaned_url)

        if DEBUG_MODE:
            print()
            print("page name:", url, "page content:", html.prettify()[:DEBUG_LOG_SIZE])
            print()

    # catch any errors (TODO: make more verbose)
    except Exception as ex:
        print(f"skipping {url} due to error: {ex}")

    if DEBUG_MODE:
        print()
        for sub_page in sub_pages:
            print(f"\t{sub_page}")
        print()


def index(browser: pw_s_api.BrowserContext, seed_list: list[str]) -> None:
    for url in seed_list:
        index_page(browser.new_page(), url)


def main() -> None:
    with pw_s_api.sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)

        seed_pages = [
            # "https://www.reddit.com",
            "https://breadleaf.github.io",
            "https://curlie.org/en",
            "https://en.wikipedia.org/wiki/Main_Page",
        ]

        index(context, seed_pages)

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
