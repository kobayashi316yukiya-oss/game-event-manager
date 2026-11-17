
import re
import urllib.request
import json
from html import unescape

URL = (
    "https://api-web.bluearchive.jp/api/news/list"
    "?typeId=0&pageNum=6&pageIndex=1"
)

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    },
)

with urllib.request.urlopen(request, timeout=20) as response:
    data = json.load(response)

if not data.get("meta", {}).get("ok"):
    raise RuntimeError("API returned an error")

rows = data.get("data", {}).get("rows", [])

for item in rows:
    content = item.get("content", "")

    # HTMLのタグを取り除いてテキストに変換
    text = re.sub(r"<[^>]+>", " ", content)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    # 開催期間・実施期間の記述を探す
    matches = re.findall(
        r"(?:開催期間|実施期間)[：:\s]*"
        r"(.{0,180}?)"
        r"(?=▼|■|【|$)",
        text,
    )

    print("=" * 50)
    print("News ID:", item.get("id"))
    print("Title:", item.get("summary"))
    print("URL:", f"https://bluearchive.jp/news/newsJump/{item.get('id')}")

    if matches:
        for match in matches:
            print("Period candidate:", match[:180])
    else:
        print("Period candidate: Not found")
