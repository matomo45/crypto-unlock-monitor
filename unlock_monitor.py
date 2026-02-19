import requests
import os
import sys

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')

def get_hl_fr(symbol):
    """HyperliquidのAPIからFRを取得（キー不要）"""
    url = "https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    # Meta情報を取得して、指定した銘柄のインデックスを探す
    payload = {"type": "metaAndAssetCtxs"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        # 銘柄名とデータの対応表を作成
        # data[0]が銘柄リスト、data[1]が市場データ
        universe = data[0]['universe']
        asset_ctxs = data[1]
        
        for i, asset in enumerate(universe):
            if asset['name'] == symbol:
                # HyperliquidのFRは1時間あたりの数値なので、8時間換算(*8)し、%表記(*100)にする
                fr_val = float(asset_ctxs[i]['funding'])
                return f"{fr_val * 8 * 100:.4f}%"
    except Exception as e:
        return f"エラー:{str(e)[:5]}"
    return "銘柄なし"

def main():
    if not SLACK_URL:
        sys.exit(1)

    # 監視銘柄（Hyperliquidに存在する銘柄）
    tokens = [
        {"symbol": "SUI", "date": "03/15"},
        {"symbol": "ARB", "date": "03/16"},
        {"symbol": "STRK", "date": "03/15"},
        {"symbol": "SOL", "date": "03/01"}
    ]

    messages = []
    for t in tokens:
        fr = get_hl_fr(t['symbol'])
        
        # 判定アイコン
        # FRが非常に高い（例：0.03%超）場合は、ショートにボーナス金利が入る「絶好機」
        if "取得失敗" not in fr and "エラー" not in fr and "銘柄なし" not in fr:
            val = float(fr.replace('%', ''))
            if val > 0.03:
                icon = "🔥【金利大】"
            elif val < 0:
                icon = "⚠️【ショート過多】"
            else:
                icon = "🔵"
        else:
            icon = "⚪"
            
        messages.append(f"{icon} *${t['symbol']}* ({t['date']}) HL-FR: `{fr}`")

    payload = {
        "text": "🔔 *最新FRレポート（Hyperliquidモード）*\n" + "\n".join(messages) + "\n\n※DEX(Hyperliquid)のリアルタイム金利"
    }
    requests.post(SLACK_URL, json=payload)

if __name__ == "__main__":
    main()
