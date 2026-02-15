import requests
import os
import sys

# 金庫から値を取得
SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CG_API_KEY = os.getenv('COINGLASS_API_KEY')

def get_fr(symbol):
    if not CG_API_KEY:
        return "Key未設定"
    
    # Coinglassで最も安定してデータが取れる形式（例：SUI）
    # API側で自動的に主要なUSDTペアを探しに行きます
    url = f"https://open-api.coinglass.com/public/v2/funding?symbol={symbol}"
    headers = {"accept": "application/json", "coinglassApi": CG_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # 成功判定
        if data.get('success') and data.get('data'):
            # 全取引所の平均FRを計算
            fr_list = []
            for item in data['data']:
                # fundingRateが空でない数値のものだけを抽出
                val = item.get('fundingRate')
                if val is not None and str(val).replace('.','').replace('-','').isdigit():
                    fr_list.append(float(val))
            
            if fr_list:
                avg_fr = sum(fr_list) / len(fr_list)
                return f"{avg_fr:.4f}%"
    except Exception:
        return "通信エラー"
    
    return "データなし"

def main():
    if not SLACK_URL:
        sys.exit(1)

    # 監視銘柄（3月の主要アンロック）
    tokens = [
        {"symbol": "SUI", "date": "03/15"},
        {"symbol": "ARB", "date": "03/16"},
        {"symbol": "STRK", "date": "03/15"},
        {"symbol": "SOL", "date": "03/01"}
    ]

    messages = []
    for t in tokens:
        fr = get_fr(t['symbol'])
        # アイコン判定：プラスなら青（ショート有利）、マイナスなら警告
        icon = "🔵" if "-" not in fr and "0." in fr else "⚠️"
        messages.append(f"{icon} *${t['symbol']}* ({t['date']}) FR: `{fr}`")

    payload = {"text": "🔔 *最新FRレポート（30日前監視）*\n" + "\n".join(messages)}
    requests.post(SLACK_URL, json=payload)

if __name__ == "__main__":
    main()
