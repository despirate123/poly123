"""Strategy utilities for filtering and selecting Polymarket opportunities."""
from __future__ import annotations

import datetime as dt
from typing import Dict, List

from polymarket_client import Market, PolymarketClient
from config import TradingConfig


def find_clear_win_markets(client: PolymarketClient, trading: TradingConfig) -> List[Dict]:
    """Identify markets where the price signals a nearly resolved outcome."""

    markets = client.fetch_markets()
    now = dt.datetime.utcnow()
    candidates: List[Dict] = []

    for market in markets:
        if not market.end_date_iso:
            continue
        resolve_time = _parse_iso(market.end_date_iso)
        if resolve_time is None:
            continue
        hours_left = (resolve_time - now).total_seconds() / 3600
        if hours_left > trading.max_time_to_resolution_hours:
            continue

        for outcome in market.outcomes:
            if outcome.best_ask is None or outcome.best_ask_size is None:
                continue
            if outcome.best_ask < trading.min_probability_price:
                continue
            if outcome.best_ask > trading.max_probability_price:
                continue
            if outcome.best_ask_size < trading.min_liquidity:
                continue

            candidates.append(
                {
                    "market_id": market.id,
                    "outcome_id": outcome.id,
                    "outcome_name": outcome.name,
                    "ask_price": outcome.best_ask,
                    "resolve_time": resolve_time.isoformat(),
                    "time_to_resolve_hours": hours_left,
                    "available_size": outcome.best_ask_size,
                    "question": market.question,
                }
            )

    return candidates


def _parse_iso(value: str):
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None
