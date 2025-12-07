"""Entry point for Polymarket clear-win trading bot."""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List

from config import DEFAULT_CONFIG_PATH, AppConfig, load_config
from polymarket_client import PolymarketClient
from risk import size_for_market
from strategy import find_clear_win_markets

LOG_PATH = Path("bot.log")
TRADES_CSV = Path("trades.csv")


def setup_logging() -> None:
    LOG_PATH.touch(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
    )


def append_trade_row(row: Dict) -> None:
    new_file = not TRADES_CSV.exists()
    with TRADES_CSV.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "market_id",
                "question",
                "outcome",
                "side",
                "price",
                "size",
                "expected_payout",
                "status",
            ],
        )
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def open_position(
    client: PolymarketClient, config: AppConfig, open_positions: List[Dict], candidate: Dict
) -> None:
    logger = logging.getLogger("bot")
    trading = config.trading
    size = size_for_market(client, trading, open_positions, candidate)
    if size < trading.min_trade_size:
        logger.info("Skipping %s due to small size (%.2f)", candidate["market_id"], size)
        return

    order = client.place_order(
        market_id=candidate["market_id"],
        outcome_id=candidate["outcome_id"],
        side="buy",
        price=candidate["ask_price"],
        size=size,
        mode=config.mode,
    )
    expected_payout = size * (1 - candidate["ask_price"])
    logger.info(
        "Opened position market=%s outcome=%s price=%.4f size=%.2f expected_payout=%.2f status=%s",
        candidate["market_id"],
        candidate.get("outcome_name", ""),
        candidate["ask_price"],
        size,
        expected_payout,
        order.get("status", "unknown"),
    )

    open_positions.append(
        {
            "market_id": candidate["market_id"],
            "outcome_id": candidate["outcome_id"],
            "outcome_name": candidate.get("outcome_name", ""),
            "entry_price": candidate["ask_price"],
            "size": size,
            "entry_time": time.time(),
        }
    )
    append_trade_row(
        {
            "timestamp": time.time(),
            "market_id": candidate["market_id"],
            "question": candidate.get("question", ""),
            "outcome": candidate.get("outcome_name", ""),
            "side": "BUY",
            "price": candidate["ask_price"],
            "size": size,
            "expected_payout": expected_payout,
            "status": order.get("status", "unknown"),
        }
    )


def run_once(client: PolymarketClient, config: AppConfig, open_positions: List[Dict]) -> None:
    logger = logging.getLogger("bot")
    candidates = find_clear_win_markets(client, config.trading)
    if not candidates:
        logger.info("No clear-win candidates found.")
        return

    for candidate in candidates:
        open_position(client, config, open_positions, candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description="Polymarket clear-win bot")
    parser.add_argument("--mode", choices=["paper", "live"], help="Run mode", default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to config file")
    parser.add_argument("--once", action="store_true", help="Run a single scan and exit")
    args = parser.parse_args()

    setup_logging()
    config = load_config(args.config)
    if args.mode:
        config.mode = args.mode

    logger = logging.getLogger("bot")
    logger.info("Starting bot in %s mode using config %s", config.mode, args.config)

    client = PolymarketClient(
        data_api_url=config.data_api_url,
        clob_api_url=config.clob_api_url,
        rpc_url=config.rpc_url,
    )

    open_positions: List[Dict] = []

    if args.once:
        run_once(client, config, open_positions)
        return

    while True:
        run_once(client, config, open_positions)
        time.sleep(config.trading.scan_interval_seconds)


if __name__ == "__main__":
    main()
