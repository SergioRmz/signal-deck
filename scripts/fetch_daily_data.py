#!/usr/bin/env python3
"""Recolecta datos contextuales diarios para el briefing matutino de Signal Deck.

Recopila:
  - Clima para CDMX (Open-Meteo, gratis, sin API key)
  - Tipo de cambio USD/MXN (Frankfurter API, gratis, sin API key)
  - Precio de Bitcoin en MXN y USD (CoinGecko, gratis, sin API key)
  - Precio del petróleo WTI (fallback a búsqueda web)

Escribe un artefacto JSON en runs/YYYY-MM-DD/daily-data.json.

Uso:
    python3 scripts/fetch_daily_data.py --run-date 2026-06-18
    python3 scripts/fetch_daily_data.py  # usa la fecha de hoy
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

# Coordenadas de Ciudad de México
CDMX_LAT = 19.4326
CDMX_LON = -99.1332
CDMX_TIMEZONE = "America/Mexico_City"

# Descripciones de códigos WMO en español
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
    """Obtiene JSON de una URL con User-Agent tipo navegador."""
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
    """Obtiene el clima de Ciudad de México desde Open-Meteo."""
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
    """Obtiene el tipo de cambio USD/MXN desde Frankfurter API."""
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
    """Obtiene el precio de Bitcoin desde CoinGecko."""
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
    """Obtiene el precio del petróleo WTI.

    Intenta Frankfurter (commodities) primero; si no está disponible,
    retorna pendiente para que la fase editorial lo complete vía web_search.
    El WTI no siempre está disponible en APIs gratuitas, así que es opcional.
    """
    # El WTI es difícil de obtener de APIs gratuitas de forma confiable.
    # Retornamos pendiente para que la fase editorial lo busque vía web_search.
    return {
        "status": "pending",
        "pair": "WTI",
        "note": "Precio WTI no disponible en APIs gratuitas. La fase editorial debe buscarlo vía web_search.",
    }


def fetch_daily_data(run_date: str, runs_dir: Path = DEFAULT_RUNS_DIR) -> dict[str, Any]:
    """Recolecta todos los datos diarios y los escribe en runs/YYYY-MM-DD/daily-data.json."""
    run_dir = runs_dir / run_date
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Obteniendo datos diarios para {run_date}...")

    weather = fetch_weather()
    print(f"  Clima: {weather['status']}")

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
    print(f"  Escrito: {output_path}")

    return artifact


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recolecta datos diarios contextuales para Signal Deck.")
    parser.add_argument(
        "--run-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Fecha objetivo, YYYY-MM-DD (por defecto: hoy).",
    )
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR, help="Directorio de runs.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    fetch_daily_data(run_date=args.run_date, runs_dir=args.runs_dir)


if __name__ == "__main__":
    main()
