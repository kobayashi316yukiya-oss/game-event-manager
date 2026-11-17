
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

URL = "https://bluearchive.jp/"


class ResourceInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.styles = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "script":
            src = attrs.get("src")
            if src:
                self.scripts.append(urljoin(URL, src))

        elif tag == "link":
            href = attrs.get("href")
            if href:
                self.styles.append(urljoin(URL, href))

        elif tag == "a":
            href = attrs.get("href")
            if href:
                self.links.append(urljoin(URL, href))


def main():
    print("=== Blue Archive Resource Inspector ===")

    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")

    inspector = ResourceInspector()
    inspector.feed(html)

    print("\n=== JavaScriptファイル ===")
    for src in inspector.scripts:
        print(src)

    print("\n=== CSS・その他リソース ===")
    for href in inspector.styles:
        print(href)

    print("\n=== ページ内リンク ===")
    for href in inspector.links:
        print(href)

    print("\n=== HTML内のキーワード周辺 ===")

    keywords = [
        "api",
        "news",
        "event",
        "script",
        "iframe"
    ]

    lower_html = html.lower()

    for keyword in keywords:
        position = lower_html.find(keyword)

        if position >= 0:
            start = max(0, position - 100)
            end = min(len(html), position + 200)

            print(f"\n[{keyword}]")
            print(html[start:end].replace("\n", " "))

    print("\n調査完了")


if __name__ == "__main__":
    main()
