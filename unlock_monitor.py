import requests
import os
import sys
from datetime import datetime, timedelta

# GitHubのSecretsから読み込み
SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CG_API_KEY = os.getenv('COINGLASS_API_KEY')

def get_fr(symbol):
    """Coinglass APIから現在のFR（8時間換算）を取得"""
    if not CG_API_KEY:
        return "N/A"
    
    url = f"https://open-api.coinglass.com/public/v2/funding?symbol={symbol}"
    headers = {"accept": "application/json", "coinglassApi": CG_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data['code'] == "0" and data['data']:
            # 複数の取引所の平均FRを取得
            fr_list = [float(x['fundingRate']) for x in data['data'] if x['fundingRate']]
            avg_fr = sum(fr_list) / len(fr_list) if fr_list else 0
            return f"{avg_fr:.4f}%"
    except:
        return "取得失敗"
    return "N/A"

def main():
    if not SLACK_URL:
        print("エラー: SLACK_WEBHOOK_URL が未設定です。")
        sys.exit(1)

    # 監視対象（3月にアンロックがある主要銘柄）
    tokens = [
        {"symbol": "SUI", "date": "2026-03-15", "pct": 1.4},
        {"symbol": "ARB", "date": "2026-03-16", "pct": 1.2},
        {"symbol": "STRK", "date": "2026-03-15", "pct": 1.3},
        {"symbol": "SOL", "date": "2026-03-01", "pct": 0.5}
    ]

    messages = []
    for t in tokens:
        fr = get_fr(t['symbol'])
        # FRがプラスなら「ショート有利」、マイナスなら「ショート過多（注意）」
        fr_icon = "🔵" if "取得失敗" not in fr and "-" not in fr else "⚠️"
        
        msg = (f"{fr_icon} *${t['symbol']}* (解放日: {t['date']})\n"
               f" ・解放量: {t['pct']}% / 現在のFR: `{fr}`")
        messages.append(msg)

    if messages:
        header = "🔔 *【30日前】アンロック銘柄 & 金利(FR)レポート*\n"
        footer = "\n> 🔵: FRプラス（ショート有利） / ⚠️: FRマイナス（コスト増）"
        requests.post(SLACK_URL, json={"text": header + "\n".join(messages) + footer})
        print("FR付きレポートを送信しました。")

if __name__ == "__main__":
    main()
