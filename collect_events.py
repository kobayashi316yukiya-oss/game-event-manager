
import re
import urllib.request
from urllib.parse import urlparse

JS_URL = (
    "https://webusstatic.yo-star.com/"
    "bluearchive_jp_web/js/chunk-vendors.e970c44.js"
)

KEYWORDS = [
    "news",
    "api",
    "axios",
    "baseURL",
    "endpoint",
    "bluearchive",
]


def main():
    print("=== Blue Archive Vendor Inspector ===")

    request = urllib.request.Request(
        JS_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        javascript = response.read().decode(
            "utf-8", errors="replace"
        )

    print("JavaScriptサイズ:", len(javascript), "文字")

    print("\n=== キーワード出現回数 ===")

    for keyword in KEYWORDS:
        count = len(
            re.findall(
                re.escape(keyword),
                javascript,
                re.IGNORECASE
            )
        )
        print(f"{keyword}: {count}")

    print("\n=== URL候補（最大30件） ===")

    urls = re.findall(
        r'https?://[^\s"\'`<>\\]+',
        javascript
    )

    found = []

    for url in urls:
        url = url.rstrip("),;]}")

        hostname = urlparse(url).hostname or ""

        if any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in [
                "google.com",
                "googleapis.com",
                "gstatic.com",
                "jsdelivr.net",
                "w3.org",
            ]
        ):
            continue

        if url not in found:
            found.append(url)

    for url in found[:30]:
        print(url[:300])

    if not found:
        print("URL候補は見つかりませんでした。")

    print("\n調査完了")


if __name__ == "__main__":
    main()
