
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser

URL = "https://bluearchive.jp/"

KEYWORDS = [
    "イベント",
    "お知らせ",
    "開催",
    "メンテナンス",
    "news",
    "event",
]


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "title":
            self.in_title = True

        if tag == "a":
            href = attributes.get("href", "")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def main():
    print("=== Blue Archive HTML Inspector ===")
    print("接続先:", URL)

    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        raw_html = response.read()
        charset = response.headers.get_content_charset() or "utf-8"

    html = raw_html.decode(charset, errors="replace")

    parser = PageInspector()
    parser.feed(html)

    print("HTMLサイズ:", len(raw_html), "bytes")
    print("ページタイトル:", parser.title.strip())
    print("リンク数:", len(parser.links))

    print("\n=== 関連リンク（最大30件） ===")

    matched_links = []

    for link in parser.links:
        if any(
            keyword.lower() in link.lower()
            for keyword in KEYWORDS
        ):
            if link not in matched_links:
                matched_links.append(link)

    for link in matched_links[:30]:
        print(link)

    if not matched_links:
        print("関連リンクは見つかりませんでした。")

    print("\n=== キーワード出現回数 ===")

    for keyword in KEYWORDS:
        count = len(
            re.findall(re.escape(keyword), html, re.IGNORECASE)
        )
        print(f"{keyword}: {count}")

    print("\n調査完了")


if __name__ == "__main__":
    main()
