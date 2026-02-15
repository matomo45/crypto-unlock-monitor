import requests
import os
import sys

def main():
    # 金庫から値が取れているかチェック
    url = os.getenv('SLACK_WEBHOOK_URL')
    api = os.getenv('CRYPTORANK_API_KEY')

    if not url:
        print("エラー: SLACK_WEBHOOK_URL が設定されていません。")
        sys.exit(1)
    
    print(f"URL取得成功: {url[:20]}...") # 最初の一部だけ表示して確認

    # テスト送信してみる
    try:
        res = requests.post(url, json={"text": "GitHub Actionsからのテスト通知です。"})
        res.raise_for_status()
        print("Slack通知に成功しました！")
    except Exception as e:
        print(f"送信エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
