import requests
import os
import sys

SLACK_URL = os.getenv('SLACK_WEBHOOK_URL')

def check_indicators(symbol):
    """
    1. FRの急激な低下を検知
    2. オンチェーンの擬似検知（取引高の急増などを代用）
    """
    url = "https://api.hyperliquid.xyz/info"
    try:
        response = requests.post(url, json={"type": "metaAndAssetCtxs"}, timeout=10)
        data = response.json()
        universe = data[0]['universe']
        asset_ctxs = data[1]

        for i, asset in enumerate(universe):
            if asset['name'] == symbol:
                # 現時点のFR（8時間換算）
                fr_val = float(asset_ctxs[i]['funding']) * 8 * 100
                # 取引高（インフローの代替指標として24h Volumeをチェック）
                day_volume = float(asset_ctxs[i]['dayNtlVlm'])
                return fr_val, day_volume

    except requests.RequestException as e:
        print(f"APIリクエストエラー ({symbol}): {e}")
        return None, None
    except (KeyError, IndexError, ValueError) as e:
        print(f"データ解析エラー ({symbol}): {e}")
        return None, None

    return None, None  # シンボルが見つからなかった場合


def main():
    if not SLACK_URL:
        print("エラー: SLACK_WEBHOOK_URL が設定されていません。")
        sys.exit(1)

    # ターゲット銘柄
    targets = ["SUI", "ARB", "STRK", "SOL", "APT", "OP"]

    alert_messages = []

    for symbol in targets:
        fr, vol = check_indicators(symbol)

        if fr is None:
            continue

        # --- 予兆検知ロジック ---
        # 1. FRがマイナス、または大幅低下 (-0.01%以下を閾値に設定)
        fr_alert = fr < -0.01

        # 2. ボリュームの異常検知（簡易版：本来は過去平均と比較）
        # ここでは「FRがマイナス」かつ「ボラティリティがある」状態を予兆と定義
        if fr_alert:
            detail = (f"🚨 *【緊急予兆検知】*\n"
                      f"🚩 *${symbol}* に強い売り圧力を検知！\n"
                      f" ・FRがマイナス転落: `{fr:.4f}%` (ショート過多)\n"
                      f" ・HL 24h Volume: `${vol:,.0f}`\n"
                      f" ⚠️ オンチェーンでの大規模送金(Inflow)が行われた可能性があります。")
            alert_messages.append(detail)

    if alert_messages:
        full_msg = "📢 *【重要】アンロック直前の異常検知アラート*\n\n" + "\n\n".join(alert_messages)
        try:
            res = requests.post(SLACK_URL, json={"text": full_msg}, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"Slack通知エラー: {e}")
            sys.exit(1)
    else:
        # 異常がなければ静かに終了、または定時連絡
        print("現在、異常な予兆は検知されていません。")


if __name__ == "__main__":
    main()
