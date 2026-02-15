import requests
import os

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CG_API_KEY = os.getenv('COINGLASS_API_KEY')

def main():
    if not SLACK_URL or not CG_API_KEY:
        requests.post(SLACK_URL, json={"text": "❌ エラー: 設定（Secrets）が読み込めていません"})
        return

    # 診断開始
    url = "https://open-api.coinglass.com/public/v2/indicator/funding_avg"
    headers = {"accept": "application/json", "coinglassApi": CG_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # ステータスコード（200なら成功、401/403なら認証失敗）
        code = response.status_code
        data = response.json()
        
        if code == 200 and data.get('success'):
            msg = "✅ API接続成功！数値も取得できています。"
        else:
            # 失敗理由をSlackに投げる
            msg = (f"⚠️ API接続に問題あり\n"
                   f"・ステータスコード: {code}\n"
                   f"・APIメッセージ: {data.get('message', 'なし')}\n"
                   f"・エラーコード: {data.get('code', 'なし')}")
            
    except Exception as e:
        msg = f"❌ 通信そのものに失敗: {str(e)}"

    requests.post(SLACK_URL, json={"text": msg})

if __name__ == "__main__":
    main()
