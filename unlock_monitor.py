import requests
import os
import sys

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CG_API_KEY = os.getenv('COINGLASS_API_KEY')

def get_all_fr_data():
    """全銘柄のFRデータを一括取得する"""
    if not CG_API_KEY:
        return None
    
    # 全銘柄の平均FRを取得するエンドポイント
    url = "https://open-api.coinglass.com/public/v2/indicator/funding_avg"
    headers = {"accept": "application/json", "coinglassApi": CG_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        if data.get('success') and data.get('data'):
            # { 'BTC': 0.01, 'ETH': 0.012, ... } という辞書形式に変換
            return {item['symbol']: item['avgFundingRate'] for item in data['data']}
    except Exception as e:
        print(f"APIエラー: {e}")
    return None

def main():
    if not SLACK_URL:
        sys.exit(1)

    # 監視銘柄
    target_symbols = ["SUI", "ARB", "STRK", "SOL"]
    unlock_dates = {"SUI": "03/15", "ARB": "03/16", "STRK": "03/15", "SOL": "03/01"}

    all_fr = get_all_fr_data()
    
    messages = []
    for symbol in target_symbols:
        # 取得したデータから銘柄を探す
        fr_val = all_fr.get(symbol) if all_fr else None
        
        if fr_val is not None:
            fr_text = f"{float(fr_val):.4f}%"
            icon = "🔵" if float(fr_val) > 0 else "⚠️"
        else:
            fr_text = "取得失敗"
            icon = "⚪"

        messages.append(f"{icon} *${symbol}* ({unlock_dates[symbol]}) FR: `{fr_text}`")

    payload = {"text": "🔔 *最新FRレポート（一括取得モード）*\n" + "\n".join(messages)}
    requests.post(SLACK_URL, json=payload)

if __name__ == "__main__":
    main()
