#!/usr/bin/env python3
"""Fetch daily contextual data for the Signal Deck morning briefing.

Collects:
  - Weather for Mexico City (Open-Meteo, free, no API key)
  - USD/MXN exchange rate (Frankfurter API, free, no API key)
  - Bitcoin price in MXN and USD (CoinGecko, free, no API key)
  - WTI crude oil price (fallback to web search snippet parsing)

Writes a single JSON artifact to runs/YYYY-MM-DD/daily-data.json.

Usage:
    python3 scripts/fetch_daily_data.py --run-date 2026-06-18
    python3 scripts/fetch_daily_data.py  # uses today's date
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_DIR = ROOT / "runs"

# Mexico City coordinates
CDMX_LAT = 19.4326
CDMX_LON = -99.1332
CDMX_TIMEZONE = "America/Mexico_City"

# WMO weather code descriptions in Spanish
WMO_CODES = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    56: "Llovizna congelada ligera",
    57: "Llovizna congelada intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    66: "Lluvia congelada ligera",
    67: "Lluvia congelada intensa",
    71: "Nieve ligera",
    73: "Nieve moderada",
    75: "Nieve intensa",
    77: "Gránulos de nieve",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos violentos",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve intensos",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo intenso",
}


def describe_wmo(code: int) -> str:
    return WMO_CODES.get(code, f"Código WMO {code}")


def fetch_json(url: str, timeout: int = 15) -> dict[str, Any]:
    """Fetch JSON from a URL with a browser-like User-Agent."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) signal-deck/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def fetch_weather() -> dict[str, Any]:
    """Fetch weather data for Mexico City from Open-Meteo."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={CDMX_LAT}&longitude={CDMX_LON}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
            f"uv_index_max,sunrise,sunset"
            f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code"
            f"&timezone={CDMX_TIMEZONE}&forecast_days=1"
        )
        data = fetch_json(url)
        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code", 0)
        return {
            "status": "ok",
            "city": "Ciudad de México",
            "current": {
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "weather_code": weather_code,
                "description": describe_wmo(weather_code),
            },
            "daily": {
                "temp_max": daily.get("temperature_2m_max", [None])[0],
                "temp_min": daily.get("temperature_2m_min", [None])[0],
                "precipitation_probability": daily.get("precipitation_probability_max", [0])[0],
                "uv_index": daily.get("uv_index_max", [None])[0],
                "sunrise": daily.get("sunrise", [None])[0],
                "sunset": daily.get("sunset", [None])[0],
            },
        }
    except Exception as exc:
        return {"status": "error", "city": "Ciudad de México", "error": str(exc)}


def fetch_usd_mxn() -> dict[str, Any]:
    """Fetch USD/MXN exchange rate from Frankfurter API."""
    try:
        data = fetch_json("https://api.frankfurter.app/latest?from=USD&to=MXN")
        rate = data.get("rates", {}).get("MXN")
        if rate is None:
            return {"status": "error", "error": "MXN rate not found in response"}
        return {
            "status": "ok",
            "pair": "USD/MXN",
            "rate": rate,
            "date": data.get("date"),
            "source": "Frankfurter API",
        }
    except Exception as exc:
        return {"status": "error", "pair": "USD/MXN", "error": str(exc)}


def fetch_btc() -> dict[str, Any]:
    """Fetch Bitcoin price from CoinGecko."""
    try:
        data = fetch_json(
            "https://api.coingecko.com/api/v3/simple/price?"
            "ids=bitcoin&vs_currencies=mxn,usd&include_24hr_change=true"
        )
        btc = data.get("bitcoin", {})
        return {
            "status": "ok",
            "pair": "BTC",
            "price_mxn": btc.get("mxn"),
            "price_usd": btc.get("usd"),
            "change_24h_pct": btc.get("mxn_24h_change"),
            "source": "CoinGecko",
        }
    except Exception as exc:
        return {"status": "error", "pair": "BTC", "error": str(exc)}


def fetch_wti() -> dict[str, Any]:
    """Fetch WTI crude oil price.

    Attempts Frankfurter (commodities) first, falls back to None if unavailable.
    WTI is not always available on free APIs, so we mark it as optional.
    """
    # WTI is hard to get from free APIs reliably.
    # We'll return a placeholder and let the editorial phase fill it via web search.
    return {
        "status": "pending",
        "pair": "WTI",
        "note": "WTI price not available from free APIs. The editorial phase should fetch it via web_search.",
    }


def fetch_daily_data(run_date: str, runs_dir: Path = DEFAULT_RUNS_DIR) -> dict[str, Any]:
    """Fetch all daily data and write to runs/YYYY-MM-DD/daily-data.json."""
    run_dir = runs_dir / run_date
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching daily data for {run_date}...")

    weather = fetch_weather()
    print(f"  Weather: {weather['status']}")

    usd_mxn = fetch_usd_mxn()
    print(f"  USD/MXN: {usd_mxn['status']}")

    btc = fetch_btc()
    print(f"  BTC: {btc['status']}")

    wti = fetch_wti()
    print(f"  WTI: {wti['status']}")

    artifact = {
        "editionDate": run_date,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "weather": weather,
        "markets": {
            "usd_mxn": usd_mxn,
            "btc": btc,
            "wti": wti,
        },
    }

    output_path = run_dir / "daily-data.json"
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    print(f"  Written: {output_path}")

    return artifact


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch daily contextual data for Signal Deck.")
    parser.add_argument(
        "--run-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target edition date, YYYY-MM-DD (default: today).",
    )
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR, help="Runs directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    fetch_daily_data(run_date=args.run_date, runs_dir=args.runs_dir)


if __name__ == "__main__":
    main()
