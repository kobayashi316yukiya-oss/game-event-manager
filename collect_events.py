
import urllib.request
import urllib.error

# ブルーアーカイブ公式サイト
URL = "https://bluearchive.jp/"

def main():
    print("=== Game Event Collector ===")
    print("対象ゲーム：ブルーアーカイブ")
    print("接続先：", URL)

    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; GameEventManager/1.0)"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            html = response.read()

            print("HTTPステータス：", response.status)
            print("取得データサイズ：", len(html), "bytes")
            print("接続テスト：成功")

    except urllib.error.HTTPError as error:
        print("HTTPエラー：", error.code)
        raise

    except urllib.error.URLError as error:
        print("接続エラー：", error.reason)
        raise


if __name__ == "__main__":
    main()
