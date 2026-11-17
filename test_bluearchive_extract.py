
import json
import re
import urllib.request
from datetime import datetime
from html import unescape
from html.parser import HTMLParser

API_URL = (
    "https://api-web.bluearchive.jp/api/news/list"
    "?typeId=0&pageNum=6&pageIndex=1"
)

DATE_PATTERN = (
    r"20\d{2}年\s*\d{1,2}月\s*\d{1,2}日"
    r"(?:\s*[\(（][月火水木金土日][\)）])?"
)

TIME_PATTERN = r"\d{1,2}:\d{2}"

PERIOD_PATTERN = re.compile(
    rf"({DATE_PATTERN})"
    rf"\s*(メンテナンス後|{TIME_PATTERN})?"
    r"\s*[～〜~\-－]\s*"
    rf"({DATE_PATTERN})"
    rf"\s*({TIME_PATTERN})?"
)

HEADINGS = (
    "開催期間",
    "実施期間",
    "回答期間",
)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br", "hr", "div", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("p", "div", "li"):
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return unescape("".join(self.parts))


def clean_text(value):
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value, time_value):
    date_numbers = re.findall(r"\d+", value)[:3]

    if len(date_numbers) != 3:
        return None

    year, month, day = map(int, date_numbers)

    if not time_value or time_value == "メンテナンス後":
        return None

    try:
        return datetime.strptime(
            f"{year}-{month}-{day} {time_value}",
            "%Y-%m-%d %H:%M",
        ).isoformat(timespec="minutes")
    except ValueError:
        return None


def extract_events(item):
    parser = TextExtractor()
    parser.feed(item.get("content") or "")

    lines = [
        clean_text(line)
        for line in parser.get_text().splitlines()
        if clean_text(line)
    ]

    events = []
    current_section = item.get("summary", "名称不明")
    previous_line = ""

    for index, line in enumerate(lines):
        # メンテナンス告知内のイベント見出しを検出
        section_match = re.match(
            r"^[（(]\d+[）)]\s*(.+)",
            line,
        )

        if section_match:
            current_section = section_match.group(1)

        # 開催期間などの見出しを検出
        heading = next(
            (h for h in HEADINGS if h in line),
            None,
        )

        if not heading:
            previous_line = line
            continue

        # 見出しの次の行に期間がある場合にも対応
        candidate = line

        if index + 1 < len(lines):
            candidate += " " + lines[index + 1]

        match = PERIOD_PATTERN.search(candidate)

        if not match:
            previous_line = line
            continue

        start_date, start_time, end_date, end_time = match.groups()

        # 個別イベント見出しがない場合はニュース概要を使う
        event_name = current_section

        events.append({
            "name": event_name,
            "start": parse_date(start_date, start_time),
            "end": parse_date(end_date, end_time),
            "start_raw": clean_text(
                f"{start_date} {start_time or ''}"
            ),
            "end_raw": clean_text(
                f"{end_date} {end_time or ''}"
            ),
            "period_type": heading,
            "source_id": item.get("id"),
            "source_url": (
                "https://bluearchive.jp/news/newsJump/"
                f"{item.get('id')}"
            ),
        })

        previous_line = line

    return events


def main():
    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(
        request, timeout=20
    ) as response:
        data = json.load(response)

    if not data.get("meta", {}).get("ok"):
        raise RuntimeError("API returned an error")

    rows = data.get("data", {}).get("rows", [])

    print("News count:", len(rows))

    total = 0

    for item in rows:
        events = extract_events(item)

        print("\n" + "=" * 60)
        print("News ID:", item.get("id"))
        print("Summary:", item.get("summary"))
        print("Extracted:", len(events))

        for event in events:
            total += 1
            print(json.dumps(
                event,
                ensure_ascii=False,
                indent=2,
            ))

    print("\nTotal extracted:", total)


if __name__ == "__main__":
    main()
