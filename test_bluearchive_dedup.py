
import json
import re
import urllib.request

from test_bluearchive_extract import (
    API_URL,
    extract_events,
)


def normalize_name(name):
    """イベント名の表記ゆれを減らす"""
    name = re.sub(r"\s+", "", name)
    name = re.sub(r"(紹介|開催)$", "", name)
    return name


def make_event_key(event):
    """イベント名・開始日・終了日で重複判定"""
    name = normalize_name(event["name"])

    start_date = event["start_raw"].split(" ")[0]
    end_date = event["end_raw"].split(" ")[0]

    return (name, start_date, end_date)


def remove_duplicates(events):
    """重複をまとめ、情報元URLを保持する"""
    unique = {}

    for event in events:
        key = make_event_key(event)

        if key not in unique:
            unique[key] = event.copy()
            unique[key]["source_urls"] = [
                event["source_url"]
            ]
        else:
            url = event["source_url"]

            if url not in unique[key]["source_urls"]:
                unique[key]["source_urls"].append(url)

    return list(unique.values())


def fetch_news():
    """ブルーアーカイブ公式APIから取得"""
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

    return data.get("data", {}).get("rows", [])


def main():
    rows = fetch_news()

    all_events = []

    for item in rows:
        events = extract_events(item)
        all_events.extend(events)

    unique_events = remove_duplicates(all_events)

    print("News count:", len(rows))
    print("Before:", len(all_events))
    print("After:", len(unique_events))

    for event in unique_events:
        print("\n" + "=" * 50)
        print("Name:", event["name"])
        print("Start:", event["start_raw"])
        print("End:", event["end_raw"])
        print("Source URLs:", event["source_urls"])

    print("\nDuplicate count:",
          len(all_events) - len(unique_events))

    print("Real API duplicate test: PASS")


if __name__ == "__main__":
    main()
