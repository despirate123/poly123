"""Risk management helpers."""
from __future__ import annotations

from typing import Dict, List

from config import TradingConfig
from polymarket_client import PolymarketClient


def get_available_capital(client: PolymarketClient, trading: TradingConfig, open_positions: List[Dict]) -> float:
    """Compute remaining capital based on balances and open exposure."""

    balances = client.get_balances()
    usdc_balance = balances.get("USDC", 0.0)
    open_exposure = sum(position.get("size", 0.0) for position in open_positions)
    capital_left = min(usdc_balance, trading.max_balance_to_use) - open_exposure
    return max(capital_left, 0.0)


def size_for_market(
    client: PolymarketClient,
    trading: TradingConfig,
    open_positions: List[Dict],
    candidate: Dict,
) -> float:
    """Determine order size respecting per-market and global exposure limits."""

    capital_left = get_available_capital(client, trading, open_positions)
    if capital_left <= 0:
        return 0.0

    size = min(trading.max_position_per_market, capital_left, candidate.get("available_size", 0.0))
    return max(0.0, size)
