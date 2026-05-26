"""
毎朝の天気予報をDiscordに通知するbot
- Open-Meteo API（無料・APIキー不要）から天気データ取得
- Discord Webhook で通知
- GitHub Actions で定時実行する想定
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Any

import requests

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# 設定（環境変数から取得）
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
LATITUDE = float(os.environ.get("LATITUDE", "35.6762"))   # デフォルト: 東京
LONGITUDE = float(os.environ.get("LONGITUDE", "139.6503"))
CITY_NAME = os.environ.get("CITY_NAME", "東京")


# WMO Weather Code → 絵文字+説明 の変換マップ
# https://open-meteo.com/en/docs#weathervariables
WEATHER_CODE_MAP: dict[int, tuple[str, str]] = {
    0: ("☀️", "快晴"),
    1: ("🌤", "晴れ"),
    2: ("⛅", "薄曇り"),
    3: ("☁️", "曇り"),
    45: ("🌫", "霧"),
    48: ("🌫", "霧（着氷）"),
    51: ("🌦", "霧雨（弱）"),
    53: ("🌦", "霧雨（中）"),
    55: ("🌧", "霧雨（強）"),
    61: ("🌧", "雨（弱）"),
    63: ("🌧", "雨"),
    65: ("🌧", "雨（強）"),
    71: ("🌨", "雪（弱）"),
    73: ("🌨", "雪"),
    75: ("❄️", "雪（強）"),
    80: ("🌦", "にわか雨（弱）"),
    81: ("🌧", "にわか雨"),
    82: ("⛈", "にわか雨（強）"),
    95: ("⛈", "雷雨"),
    96: ("⛈", "雷雨（雹を伴う）"),
    99: ("⛈", "激しい雷雨"),
}


def fetch_weather(lat: float, lon: float) -> dict[str, Any]:
    """Open-Meteo APIから本日の天気予報を取得"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Tokyo",
        "forecast_days": 1,
    }

    logger.info(f"天気データ取得中: lat={lat}, lon={lon}")
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()


def build_embed(weather_data: dict[str, Any], city: str) -> dict[str, Any]:
    """Discord Webhook用のEmbedメッセージを組み立てる"""
    daily = weather_data["daily"]
    code = daily["weather_code"][0]
    t_max = daily["temperature_2m_max"][0]
    t_min = daily["temperature_2m_min"][0]
    precip_prob = daily["precipitation_probability_max"][0]

    emoji, description = WEATHER_CODE_MAP.get(code, ("❓", "不明"))
    date_str = datetime.now().strftime("%m月%d日(%a)")

    # 降水確率に応じて色を変える（Discordのembedはcolorを整数で指定）
    if precip_prob >= 70:
        color = 0x3498DB  # 青（雨）
    elif precip_prob >= 30:
        color = 0xF1C40F  # 黄（降るかも）
    else:
        color = 0xE67E22  # オレンジ（晴れ）

    description_text = (
        f"{emoji} **{description}**\n"
        f"🌡 最高 **{t_max}℃** / 最低 **{t_min}℃**\n"
        f"💧 降水確率 **{precip_prob}%**"
    )
    if precip_prob >= 50:
        description_text += "\n\n☂️ **傘を持って出かけましょう**"

    embed = {
        "title": f"☀️ {date_str} の{city}の天気",
        "description": description_text,
        "color": color,
        "footer": {"text": "Powered by Open-Meteo"},
    }
    return embed


def post_to_discord(webhook_url: str, embed: dict[str, Any]) -> None:
    """Discord Webhookへ投稿"""
    payload = {
        "username": "天気予報bot",
        "embeds": [embed],
    }
    response = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Discordへの送信完了")


def main() -> int:
    if not DISCORD_WEBHOOK_URL:
        logger.error("環境変数 DISCORD_WEBHOOK_URL が設定されていません")
        return 1

    try:
        weather = fetch_weather(LATITUDE, LONGITUDE)
        embed = build_embed(weather, CITY_NAME)
        logger.info(f"送信内容: {json.dumps(embed, ensure_ascii=False, indent=2)}")
        post_to_discord(DISCORD_WEBHOOK_URL, embed)
        return 0
    except requests.RequestException as e:
        logger.error(f"HTTP通信エラー: {e}")
        return 1
    except (KeyError, IndexError) as e:
        logger.error(f"レスポンス形式エラー: {e}")
        return 1
    except Exception as e:
        logger.exception(f"予期せぬエラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
