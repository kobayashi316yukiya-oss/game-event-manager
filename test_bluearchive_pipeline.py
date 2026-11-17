
import json
from datetime import date

from test_bluearchive_extract import extract_events
from test_bluearchive_dedup import (
    fetch_news,
    remove_duplicates,
)
from test_bluearchive_firestore_format import (
    to_firestore_document,
)


def validate_document(document):
    """Firestore登録前のデータ検証"""

    required_fields = [
        "title",
        "gameId",
        "startDate",
        "endDate",
        "status",
    ]

    for field in required_fields:
        if not document.get(field):
            return False, f"Missing field: {field}"

    try:
        start_date = date.fromisoformat(
            document["startDate"]
        )
        end_date = date.fromisoformat(
            document["endDate"]
        )
    except (ValueError, TypeError):
        return False, "Invalid date"

    if start_date > end_date:
        return False, "Start date is after end date"

    if document["status"] != "pending":
        return False, "Invalid status"

    return True, "OK"


def main():
    print("=== Blue Archive Event Pipeline ===")

    # 1. 公式ニュースを取得
    rows = fetch_news()
    print("News count:", len(rows))

    # 2. イベント情報を抽出
    all_events = []

    for item in rows:
        events = extract_events(item)
        all_events.extend(events)

    print("Extracted events:", len(all_events))

    # 3. 重複イベントを統合
    unique_events = remove_duplicates(all_events)

    print("Unique events:", len(unique_events))

    # 4. Firestore形式に変換・検証
    valid_documents = []
    skipped_documents = []

    for event in unique_events:
        document = to_firestore_document(event)

        valid, reason = validate_document(document)

        if valid:
            valid_documents.append(document)
        else:
            skipped_documents.append({
                "title": document.get("title"),
                "reason": reason,
            })

    # 5. 登録予定データを表示
    print("\n=== Firestore Preview ===")

    print(json.dumps(
        valid_documents,
        ensure_ascii=False,
        indent=2,
    ))

    # 6. 集計
    print("\n=== Summary ===")
    print("News:", len(rows))
    print("Extracted:", len(all_events))
    print("Unique:", len(unique_events))
    print("Valid:", len(valid_documents))
    print("Skipped:", len(skipped_documents))

    if skipped_documents:
        print("\n=== Skipped Documents ===")
        print(json.dumps(
            skipped_documents,
            ensure_ascii=False,
            indent=2,
        ))

    print("\nPipeline test: PASS")


if __name__ == "__main__":
    main()
