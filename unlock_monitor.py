import requests
import os
import sys
from datetime import datetime

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')


def check_indicators(symbol):
    url = "https://api.hyperliquid.xyz/info"
    try:
        response = requests.post(url, json={"type": "metaAndAssetCtxs"}, timeout=10)
        data = response.json()
        universe = data[0]['universe']
        asset_ctxs = data[1]
        for i, asset in enumerate(universe):
            if asset['name'] == symbol:
                fr_val = float(asset_ctxs[i]['funding']) * 8 * 100
                vol = float(asset_ctxs[i]['dayNtlVlm'])
                return fr_val, vol
    except requests.RequestException as e:
        print(f"APIリクエストエラー ({symbol}): {e}")
        return None, None
    except (KeyError, IndexError, ValueError) as e:
        print(f"データ解析エラー ({symbol}): {e}")
        return None, None
    return None, None


def send_slack(message: str) -> None:
    try:
        res = requests.post(SLACK_URL, json={"text": message}, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Slack通知エラー: {e}")
        sys.exit(1)


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

    # UTC 0時 = 日本時間 9時（GitHub ActionsのUTC基準）
    now_hour = datetime.utcnow().hour

    alert_messages = []
    status_messages = []

    for item in targets:
        fr, vol = check_indicators(item['symbol'])
        if fr is None:
            continue

        if fr < -0.01:
            alert_messages.append(
                f"🚨 *【緊急予兆】${item['symbol']}*\n"
                f" ・FR: `{fr:.4f}%` / Vol: `${vol:,.0f}`\n"
                f" ⚠️ 売りヘッジ急増。インフローの可能性大。"
            )

        status_icon = "⚪" if fr >= 0 else "🔴"
        status_messages.append(
            f"{status_icon} *${item['symbol']}* ({item['date']}) FR: `{fr:.4f}%`"
        )

    # A: 異常がある場合は即時通知
    if alert_messages:
        send_slack("📢 *【異常検知アラート】*\n\n" + "\n\n".join(alert_messages))

    # B: UTC 0時（日本時間 9時）のみ定時レポートを送信
    if now_hour == 0:
        send_slack("📅 *【定時】アンロック銘柄モニタリング*\n\n" + "\n".join(status_messages))


if __name__ == "__main__":
    main()
