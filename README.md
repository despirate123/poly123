# Polymarket Clear-Win Bot

Experimental trading bot that searches for near-resolved Polymarket markets (prices ~0.97–0.995) and buys the dominant outcome with tight risk controls.

## Features
- Scans Polymarket CLOB markets for "clear-win" opportunities based on price and time-to-resolution filters.
- Paper-trading mode for dry runs; live mode placeholder for real execution.
- Simple risk management limiting per-market size and overall exposure.
- Logging to console and `bot.log`, trade CSV at `trades.csv`.

## Project structure
- `config.py` – configuration loading from YAML/JSON plus environment overrides.
- `config.yaml` – default configuration values (safe to edit).
- `polymarket_client.py` – HTTP wrapper for data and order endpoints with retries.
- `strategy.py` – market scanning logic for clear-win filters.
- `risk.py` – capital checks and position sizing.
- `main.py` – CLI entry point.
- `.env.example` – example environment variables.

## Requirements
- Python 3.10+
- Recommended dependencies (install via pip):
  - `httpx`
  - `python-dotenv`
  - `pyyaml`

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install httpx python-dotenv pyyaml
   ```
2. Copy `.env.example` to `.env` and fill in values (never commit your real private key):
   ```bash
   cp .env.example .env
   ```
3. Adjust `config.yaml` if needed (API URLs, thresholds, scan interval).

## Running the bot
- Paper mode one-shot scan:
  ```bash
  python main.py --mode=paper --once
  ```
- Paper mode continuous scanning (default 60s interval):
  ```bash
  python main.py --mode=paper
  ```
- Live mode (requires funded wallet and RPC):
  ```bash
  python main.py --mode=live
  ```

The bot logs actions to `bot.log` and appends trade attempts to `trades.csv`.

## Safety and disclaimer
This repository is **experimental**. Using it with real funds is entirely at your own risk. There is **no guarantee of profit**, and you may lose money. Always dry-run in paper mode before considering live execution.
