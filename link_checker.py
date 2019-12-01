import argparse
import requests
from bs4 import BeautifulSoup


class LinkChecker:
    def __init__(self, url):
        self._base_url = url
        self._links = set()

    def check(self, verbose):
        self.find_links(self._base_url)

        for link in self._links:
            url = self.build_url(link)
            r = requests.get(url)
            if r.status_code != 200 or verbose:
                print("{}: {}".format(url, r.status_code))
            else:
                print(".", flush=True, end="")

        print("\nChecked {} links".format(len(self._links)))

    def find_links(self, url):
        if not url.startswith(self._base_url):
            return

        print("Checking {}".format(url))

        # TODO: handle broken links
        # TODO: only check links once
        r = requests.get(url)
        body = r.text
        soup = BeautifulSoup(body, 'lxml')
        links = soup.find_all("a")

        for link in links:
            url = link.get('href')
            if url not in self._links:
                is_internal = self.validate_internal(url)
                if is_internal:
                    self._links.add(url)
                    self.find_links(self.build_url(url))

        imgs = soup.find_all("img")

        for img in imgs:
            url = img.get("src")
            if url not in self._links:
                self._links.add(url)

    def validate_internal(self, link):
        status = True

        if link.startswith(self._base_url):
            return True

        # Hack: try to cater for links outside this site
        ext_prefixes = ["http", "www.", "mailto:"]

        for ext in ext_prefixes:
            if link.startswith(ext):
                status = False
                break

        return status

    def build_url(self, link):
        if link.startswith(self._base_url):
            return link.strip()

        if link.startswith("/"):
            link = link[1:]

        return self._base_url + "/" + link.strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args()

    LinkChecker(args.url).check(args.verbose)
