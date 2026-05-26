# 天気予報 Discord通知bot

毎朝、指定地点の天気予報を Discord に自動投稿する Python スクリプトです。
GitHub Actions を使って完全無料・サーバーレスで定期実行できます。

## 機能

- 📍 緯度経度を指定して、その地点の天気を取得
- 🌤 天気・最高/最低気温・降水確率を Discord の Embed メッセージで投稿
- ☂️ 降水確率が 50% 以上なら傘リマインダーを自動追加
- 🎨 降水確率に応じてメッセージの色が変化（晴れ=オレンジ / 雨=青）
- ⏰ GitHub Actions で毎朝7時に自動実行
- 🆓 完全無料（Open-Meteo API は APIキー不要、GitHub Actions の Public リポジトリ枠を使用）

## 必要なもの

- Python 3.10 以上
- Discord サーバー（Webhook URL）
- GitHub アカウント（定期実行する場合）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/[your-id]/weather-discord-bot.git
cd weather-discord-bot
pip install -r requirements.txt
```

### 2. Discord Webhook を作成

1. Discord で通知したいチャンネルを開く
2. チャンネル名の横の歯車アイコン → 連携サービス → ウェブフック
3. 新しいウェブフック → 名前を設定 → URLをコピー

### 3. ローカルで動作確認

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export LATITUDE="35.6762"        # 東京
export LONGITUDE="139.6503"
export CITY_NAME="東京"
python main.py
```

### 4. GitHub Actions で定期実行（推奨）

1. GitHub リポジトリの Settings → Secrets and variables → Actions
2. `DISCORD_WEBHOOK_URL` を Secret として登録
3. `.github/workflows/daily.yml` をコミット
4. 毎朝7時（JST）に自動実行されます

## カスタマイズ例

| やりたいこと | 変更箇所 |
|---|---|
| 地点を変える | 環境変数 `LATITUDE` `LONGITUDE` `CITY_NAME` |
| 通知時刻を変える | `.github/workflows/daily.yml` の cron |
| Slack / LINE に通知 | `post_to_discord` を他のwebhook用に差し替え |
| 週末はスキップ | `main()` の冒頭に曜日チェックを追加 |
| 1週間先まで通知 | API パラメータ `forecast_days` を変更 |

## ファイル構成

```
weather-discord-bot/
├── main.py                    # メインスクリプト
├── requirements.txt           # 依存パッケージ
├── .github/workflows/daily.yml  # GitHub Actions 定期実行設定
└── README.md
```

## ライセンス

MIT
