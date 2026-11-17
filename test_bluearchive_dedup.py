
import re

from test_bluearchive_extract import extract_events


def normalize_name(name):
    """イベント名の表記ゆれを減らす"""
    name = re.sub(r"\s+", "", name)
    name = re.sub(r"(紹介|開催)$", "", name)
    return name


def make_event_key(event):
    """ニュースIDに依存しない重複判定キー"""
    name = normalize_name(event["name"])

    # メンテナンス後など、時刻不明の場合も比較できるようにする
    start_date = event["start_raw"].split(" ")[0]
    end_date = event["end_raw"].split(" ")[0]

    return (name, start_date, end_date)


def remove_duplicates(events):
    unique = {}

    for event in events:
        key = make_event_key(event)

        if key not in unique:
            unique[key] = event

    return list(unique.values())


def main():
    sample_events = [
        {
            "name": "【復刻イベント】「誰が為の芸術～偽飾の絵画と美学の行方～」紹介",
            "start_raw": "2026年11月11日(水) メンテナンス後",
            "end_raw": "2026年11月25日(水) 10:59",
            "source_id": 710,
        },
        {
            "name": "【復刻イベント】「誰が為の芸術～偽飾の絵画と美学の行方～」開催",
            "start_raw": "2026年11月11日(水) メンテナンス後",
            "end_raw": "2026年11月25日(水) 10:59",
            "source_id": 709,
        },
        {
            "name": "キヴォトス合同火力演習「防御演習」開催",
            "start_raw": "2026年11月11日(水) メンテナンス後",
            "end_raw": "2026年11月18日(水) 3:59",
            "source_id": 709,
        },
    ]

    unique_events = remove_duplicates(sample_events)

    print("Before:", len(sample_events))
    print("After:", len(unique_events))

    for event in unique_events:
        print(
            "ID:", event["source_id"],
            "| Name:", event["name"],
        )

    assert len(unique_events) == 2, (
        "Duplicate detection failed"
    )

    print("Duplicate test: PASS")


if __name__ == "__main__":
    main()
