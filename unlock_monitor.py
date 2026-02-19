import requests
import os
import sys

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')

def check_indicators(symbol):
    """
    HyperliquidからFRと取引高(Volume)を取得
    """
    url = "https://api.hyperliquid.xyz/info"
    try:
        response = requests.post(url, json={"type": "metaAndAssetCtxs"}, timeout=10)
        data = response.json()
        universe = data[0]['universe']
        asset_ctxs = data[1]
        for i, asset in enumerate(universe):
            if asset['name'] == symbol:
                fr_val = float(asset_ctxs[i]['funding']) * 8 * 100
                day_volume = float(asset_ctxs[i]['dayNtlVlm'])
                return fr_val, day_volume
    except requests.RequestException as e:
        print(f"APIリクエストエラー ({symbol}): {e}")
        return None, None
    except (KeyError, IndexError, ValueError) as e:
        print(f"データ解析エラー ({symbol}): {e}")
        return None, None
    return None, None


def main():
    if not SLACK_URL:
        print("エラー: SLACK_WEBHOOK_URL が設定されていません。")
        sys.exit(1)

    targets = [
        {"symbol": "SUI",  "date": "03/01"},
        {"symbol": "SOL",  "date": "03/01"},
        {"symbol": "APT",  "date": "03/12"},
        {"symbol": "ARB",  "date": "03/16"},
        {"symbol": "STRK", "date": "03/15"},
        {"symbol": "OP",   "date": "03/29"}
    ]

    alert_messages = []

    for item in targets:
        symbol = item['symbol']
        fr, vol = check_indicators(symbol)
        if fr is None:
            continue

        if fr < -0.01:
            msg = (f"🚨 *【緊急予兆検知：強い売り圧力】*\n"
                   f"🚩 *${symbol}* (アンロック予定: {item['date']})\n"
                   f" ・FRがマイナス転落: `{fr:.4f}%` (ショート過多)\n"
                   f" ・24h Volume: `${vol:,.0f}`\n"
                   f" ⚠️ DEXでの売りヘッジが急増中。取引所へのインフローが行われた可能性があります。")
            alert_messages.append(msg)

    if alert_messages:
        full_msg = "📢 *【重要】アンロック直前のオンチェーン/市場異常検知*\n\n" + "\n\n".join(alert_messages)
        try:
            res = requests.post(SLACK_URL, json={"text": full_msg}, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"Slack通知エラー: {e}")
            sys.exit(1)
    else:
        print("現在、対象銘柄に特筆すべき異常値は検知されていません。")


if __name__ == "__main__":
    main()
