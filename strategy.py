"""Strategy utilities for filtering and selecting Polymarket opportunities."""
from __future__ import annotations

import datetime as dt
import logging
from typing import Dict, List

from polymarket_client import Market, PolymarketClient
from config import TradingConfig


def find_clear_win_markets(client: PolymarketClient, trading: TradingConfig) -> List[Dict]:
    """Identify markets where the price signals a nearly resolved outcome."""

    logger = logging.getLogger("strategy")
    markets = client.fetch_markets()
    now = dt.datetime.utcnow()
    candidates: List[Dict] = []
    reason_counts = {
        "missing_end": 0,
        "bad_end": 0,
        "too_late": 0,
        "no_best_ask": 0,
        "price_low": 0,
        "price_high": 0,
        "low_liquidity": 0,
    }
    near_price_hits: List[Dict] = []

    for market in markets:
        if not market.end_date_iso:
            reason_counts["missing_end"] += 1
            continue
        resolve_time = _parse_iso(market.end_date_iso)
        if resolve_time is None:
            reason_counts["bad_end"] += 1
            continue
        hours_left = (resolve_time - now).total_seconds() / 3600
        if hours_left > trading.max_time_to_resolution_hours:
            reason_counts["too_late"] += 1
            continue

        for outcome in market.outcomes:
            if outcome.best_ask is None or outcome.best_ask_size is None:
                reason_counts["no_best_ask"] += 1
                continue
            if outcome.best_ask < trading.min_probability_price:
                reason_counts["price_low"] += 1
                if outcome.best_ask >= trading.min_probability_price - 0.05:
                    near_price_hits.append(
                        {
                            "market": market.question,
                            "outcome": outcome.name,
                            "best_ask": outcome.best_ask,
                            "hours_left": hours_left,
                            "liq": outcome.best_ask_size,
                        }
                    )
                continue
            if outcome.best_ask > trading.max_probability_price:
                reason_counts["price_high"] += 1
                continue
            if outcome.best_ask_size < trading.min_liquidity:
                reason_counts["low_liquidity"] += 1
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

    if not candidates:
        top_near = sorted(near_price_hits, key=lambda x: x["best_ask"], reverse=True)[:5]
        if top_near:
            logger.info(
                "Nearest markets below threshold (top %d): %s",
                len(top_near),
                "; ".join(
                    f"{item['market']} | {item['outcome']} ask={item['best_ask']:.4f} liq={item['liq']:.2f} ttr={item['hours_left']:.1f}h"
                    for item in top_near
                ),
            )
        logger.info(
            "Filtered %d markets; reasons: %s",
            len(markets),
            ", ".join(f"{k}={v}" for k, v in reason_counts.items()),
        )

    return candidates


def _parse_iso(value: str):
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None
