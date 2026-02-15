import requests
import os
import sys
from datetime import datetime, timedelta

def get_token_data():
    """
    本来はAPIから取得しますが、まずは確実に動くよう
    主要銘柄の3月アンロック情報をプリセットしています。
    """
    return [
        {"symbol": "SUI", "date": "2026-03-15", "pct": 1.4, "vc_roi": 7.5},
        {"symbol": "ARB", "date": "2026-03-16", "pct": 1.2, "vc_roi": 5.2},
        {"symbol": "STRK", "date": "2026-03-15", "pct": 1.3, "vc_roi": 2.8},
        {"symbol": "SOL", "date": "2026-03-01", "pct": 0.5, "vc_roi": 100}
    ]

def main():
    url = os.getenv('SLACK_WEBHOOK_URL')
    if not url:
        print("エラー: SLACK_WEBHOOK_URL が未設定です。")
        sys.exit(1)

    tokens = get_token_data()
    now = datetime.now()
    target_date = now + timedelta(days=30)
    
    messages = []
    for t in tokens:
        unlock_date = datetime.strptime(t['date'], '%Y-%m-%d')
        # 今日から30日前後のものだけをピックアップ
        if now <= unlock_date <= target_date + timedelta(days=5):
            priority = "🚨" if t['pct'] >= 1.0 else "ℹ️"
            msg = (f"{priority} *${t['symbol']}*\n"
                   f" ・解放日: {t['date']} (約30日後)\n"
                   f" ・解放量: {t['pct']}% / VC推定利益: {t['vc_roi']}倍")
            messages.append(msg)

    if messages:
        header = "🔔 *【30日前】アンロック警戒リスト*\n"
        full_message = header + "\n" + "\n".join(messages)
        requests.post(url, json={"text": full_message})
        print("実戦用レポートを送信しました。")
    else:
        print("現在、30日以内に該当する大型アンロックはありません。")

if __name__ == "__main__":
    main()
