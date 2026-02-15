import requests
import json
import os
from datetime import datetime, timedelta

# GitHubの環境変数から情報を読み込む（コードに直接書かないため）
SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CRYPTORANK_API = os.getenv('CRYPTORANK_API_KEY')
COINGLASS_API = os.getenv('COINGLASS_API_KEY')

def get_unlocks():
    # 30日後のアンロック銘柄を特定するロジック
    # ここでは例として主要なL1/L2銘柄を対象にします
    target_coins = ['SUI', 'ARB', 'STRK', 'SOL']
    # 実際にはCryptoRank API等を叩いてデータを取得します
    return [
        {"symbol": "SUI", "date": "2026-03-15", "pct": 1.4, "vc_roi": 7.5},
        {"symbol": "ARB", "date": "2026-03-16", "pct": 1.2, "vc_roi": 5.2}
    ]

def get_market_data(symbol):
    # Coinglass API等でFRやインフローを取得
    # 今回はシミュレーション値を返します
    return {"fr": -0.0001, "inflow": "High"}

def main():
    unlocks = get_unlocks()
    messages = []

    for coin in unlocks:
        market = get_market_data(coin['symbol'])
        # 異常検知ロジック
        status = "🔴 警戒" if market['fr'] < 0 or market['inflow'] == "High" else "🟢 安定"
        
        msg = (f"{status} *${coin['symbol']}* ({coin['date']})\n"
               f" ・解放量: {coin['pct']}% / VC利益: {coin['vc_roi']}倍\n"
               f" ・現在FR: {market['fr']}% / 取引所流入: {market['inflow']}")
        messages.append(msg)

    if messages:
        payload = {"text": "🔔 *【30日前】アンロック・市場予兆レポート*\n\n" + "\n\n".join(messages)}
        requests.post(SLACK_URL, data=json.dumps(payload))

if __name__ == "__main__":
    main()