
import json
import re


def extract_date(raw_value):
    """日本語の日付からYYYY-MM-DDを取り出す"""
    match = re.search(
        r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日",
        raw_value or "",
    )

    if not match:
        return None

    year, month, day = map(int, match.groups())

    return f"{year:04d}-{month:02d}-{day:02d}"


def to_firestore_document(event):
    """既存のFirestore形式に変換する"""
    return {
        "title": event["name"],
        "gameId": "blue_archive",
        "startDate": extract_date(event["start_raw"]),
        "endDate": extract_date(event["end_raw"]),
        "status": "pending",
        "sourceUrls": event.get("source_urls", []),
    }


def main():
    sample_event = {
        "name": "【復刻イベント】誰が為の芸術",
        "start_raw": "2026年11月11日(水) メンテナンス後",
        "end_raw": "2026年11月25日(水) 10:59",
        "source_urls": [
            "https://bluearchive.jp/news/newsJump/710",
            "https://bluearchive.jp/news/newsJump/709",
        ],
    }

    document = to_firestore_document(sample_event)

    print(json.dumps(
        document,
        ensure_ascii=False,
        indent=2,
    ))

    assert document["startDate"] == "2026-11-11"
    assert document["endDate"] == "2026-11-25"
    assert document["status"] == "pending"

    print("\nFirestore format test: PASS")


if __name__ == "__main__":
    main()
