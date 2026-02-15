import requests
import os
import sys

# 名前を正確に合わせる
SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')
CG_API_KEY = os.getenv('COINGLASS_API_KEY')

def get_fr(symbol):
    if not CG_API_KEY:
        return "Key未設定"
    
    # シンボルを 'SUI' から 'SUI/USDT' 形式に変更（Coinglassの仕様に合わせる）
    url = f"https://open-api.coinglass.com/public/v2/funding?symbol={symbol}/USDT"
    headers = {"accept": "application/json", "coinglassApi": CG_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # APIキーが間違っている場合はここで判明する
        if data.get('code') == "50001":
            return "Keyエラー"
            
        if data.get('success') and data.get('data'):
            # BinanceやBybitなどの主要なFRを抽出
            fr_list = [float(x['fundingRate']) for x in data['data'] if x.get('fundingRate')]
            if fr_list:
                avg_fr = sum(fr_list) / len(fr_list)
                return f"{avg_fr:.4f}%"
    except Exception as e:
        return f"エラー:{str(e)[:5]}"
    return "データなし"

def main():
    if not SLACK_URL:
        sys.exit(1)

    # 監視銘柄
    tokens = [
        {"symbol": "SUI", "date": "03/15"},
        {"symbol": "ARB", "date": "03/16"},
        {"symbol": "STRK", "date": "03/15"},
        {"symbol": "SOL", "date": "03/01"}
    ]

    messages = []
    for t in tokens:
        fr = get_fr(t['symbol'])
        # 判定アイコン
        icon = "🔵" if "0." in fr and "-" not in fr else "⚠️"
        messages.append(f"{icon} *${t['symbol']}* ({t['date']}) FR: `{fr}`")

    payload = {"text": "🔔 *最新FRレポート*\n" + "\n".join(messages)}
    requests.post(SLACK_URL, json=payload)

if __name__ == "__main__":
    main()
