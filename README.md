# Polymarket Clear-Win Bot

Experimental trading bot that searches for near-resolved Polymarket markets (prices ~0.97–0.995) and buys the dominant outcome with tight risk controls.

Экспериментальный торговый бот, который ищет почти решённые рынки Polymarket (цены ~0.97–0.995) и покупает очевидный исход с аккуратным риск-менеджментом.

## Features
- Scans Polymarket CLOB markets for "clear-win" opportunities based on price and time-to-resolution filters.
- Paper-trading mode for dry runs; live mode placeholder for real execution.
- Simple risk management limiting per-market size and overall exposure.
- Logging to console and `bot.log`, trade CSV at `trades.csv`.

## Возможности
- Сканиует CLOB-рынки Polymarket в поисках "почти решённых" ситуаций по цене и времени до резолва.
- Режим paper-trading для тестов; live-режим как заготовка для реальных сделок.
- Простой риск-менеджмент: лимиты на позицию и общую экспозицию.
- Логи в консоль и `bot.log`, сделки в `trades.csv`.

## Project structure
- `config.py` – configuration loading from YAML/JSON plus environment overrides.
- `config.yaml` – default configuration values (safe to edit).
- `polymarket_client.py` – HTTP wrapper for data and order endpoints with retries.
- `strategy.py` – market scanning logic for clear-win filters.
- `risk.py` – capital checks and position sizing.
- `main.py` – CLI entry point.
- `.env.example` – example environment variables.

## Структура проекта
- `config.py` — загрузка конфигурации из YAML/JSON с переопределениями через переменные окружения.
- `config.yaml` — значения по умолчанию (можно смело редактировать).
- `polymarket_client.py` — HTTP-обёртка для данных и ордеров с ретраями.
- `strategy.py` — логика поиска "почти решённых" рынков.
- `risk.py` — проверки капитала и расчёт размера позиции.
- `main.py` — CLI-точка входа.
- `.env.example` — пример переменных окружения.

## Requirements
- Python 3.10+
- Recommended dependencies (install via pip):
  - `httpx`
  - `python-dotenv`
  - `pyyaml`

## Требования
- Python 3.10+
- Рекомендуемые зависимости (устанавливаются через pip):
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
   - Insert your Polymarket wallet key into the `PRIVATE_KEY` variable inside `.env` (only needed for `--mode=live`).
   - If you stay in paper mode you can leave `PRIVATE_KEY` blank; it will never be used to sign transactions.
3. Adjust `config.yaml` if needed (API URLs, thresholds, scan interval).

## Настройка
1. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install httpx python-dotenv pyyaml
   ```
2. Скопируйте `.env.example` в `.env` и заполните значения (никогда не коммитьте реальный приватный ключ):
   ```bash
   cp .env.example .env
   ```
   - Вставьте приватный ключ кошелька Polymarket в переменную `PRIVATE_KEY` внутри `.env` (нужен только для `--mode=live`).
   - В paper-режиме `PRIVATE_KEY` можно оставить пустым — он не используется для подписания транзакций.
3. При необходимости измените `config.yaml` (URL API, пороги, интервал сканирования).

## Running the bot
- The entry point is `main.py`.
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

## Запуск бота
- Точка входа — `main.py`.
- Paper-режим, один проход:
  ```bash
  python main.py --mode=paper --once
  ```
- Paper-режим, постоянное сканирование (интервал по умолчанию 60с):
  ```bash
  python main.py --mode=paper
  ```
- Live-режим (нужен кошелёк с балансом и RPC):
  ```bash
  python main.py --mode=live
  ```

The bot logs actions to `bot.log` and appends trade attempts to `trades.csv`.

Бот пишет логи в `bot.log` и добавляет попытки сделок в `trades.csv`.

## Safety and disclaimer
This repository is **experimental**. Using it with real funds is entirely at your own risk. There is **no guarantee of profit**, and you may lose money. Always dry-run in paper mode before considering live execution.

## Безопасность и дисклеймер
Этот репозиторий **экспериментальный**. Использование с реальными деньгами — полностью на ваш риск. **Нет гарантии прибыли**, и вы можете потерять средства. Всегда запускайте тесты в paper-режиме перед тем как рассматривать live-торговлю.
