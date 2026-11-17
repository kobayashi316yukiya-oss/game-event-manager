
import re
import urllib.request

JS_URL = (
    "https://webusstatic.yo-star.com/"
    "bluearchive_jp_web/js/app.f992dae9.js"
)

KEYWORDS = [
    "news",
    "axios",
    "getNews",
    "newsList",
    "newsDetail",
]


def main():
    print("=== Blue Archive News Code Inspector ===")

    request = urllib.request.Request(
        JS_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        javascript = response.read().decode(
            "utf-8", errors="replace"
        )

    for keyword in KEYWORDS:
        print(f"\n=== {keyword} の周辺コード ===")

        matches = list(
            re.finditer(
                re.escape(keyword),
                javascript,
                re.IGNORECASE
            )
        )

        print("出現回数:", len(matches))

        # ログが長くなりすぎないよう最大5件
        for index, match in enumerate(matches[:5], start=1):
            start = max(0, match.start() - 180)
            end = min(len(javascript), match.end() + 250)

            snippet = javascript[start:end]
            snippet = snippet.replace("\n", " ")

            print(f"\n[{index}]")
            print(snippet)

    print("\n調査完了")


if __name__ == "__main__":
    main()
