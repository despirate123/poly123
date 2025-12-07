"""Lightweight Polymarket client for data and order placement."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MarketOutcome:
    """Outcome information including order book levels."""

    id: str
    name: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    best_ask_size: Optional[float]


@dataclass
class Market:
    """Simplified market representation from the Polymarket API."""

    id: str
    question: str
    end_date_iso: str
    outcomes: List[MarketOutcome]


class PolymarketClient:
    """HTTP client wrapper to access Polymarket APIs and CLOB endpoints."""

    def __init__(self, data_api_url: str, clob_api_url: str, rpc_url: str, timeout: float = 10.0):
        self.data_api_url = data_api_url.rstrip("/")
        self.clob_api_url = clob_api_url.rstrip("/")
        self.rpc_url = rpc_url
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout)

    def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Perform HTTP request with simple retry and exponential backoff."""

        attempts = 0
        backoff = 1.0
        while attempts < 3:
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except Exception as exc:  # noqa: BLE001
                attempts += 1
                logger.error("API request failed (%s): %s", url, exc)
                if attempts >= 3:
                    raise
                time.sleep(backoff)
                backoff *= 2

        raise RuntimeError("Failed request after retries")

    def fetch_markets(self) -> List[Market]:
        """Return a list of active markets from the Polymarket data API."""

        response = self._request_with_retry("GET", self.data_api_url)
        data = response.json()
        markets: List[Market] = []

        for item in data if isinstance(data, list) else data.get("markets", []):
            outcomes: List[MarketOutcome] = []
            for outcome in item.get("outcomes", []):
                order_book = outcome.get("orderBook", {}) or {}
                best_bid, best_ask, best_ask_size = _extract_best_levels(outcome, order_book)
                outcomes.append(
                    MarketOutcome(
                        id=str(outcome.get("id", outcome.get("tokenId", ""))),
                        name=outcome.get("name", ""),
                        best_bid=best_bid,
                        best_ask=best_ask,
                        best_ask_size=best_ask_size,
                    )
                )

            markets.append(
                Market(
                    id=str(item.get("id")),
                    question=item.get("question", item.get("title", "")),
                    end_date_iso=_pick_end_date(item),
                    outcomes=outcomes,
                )
            )

        return markets

    def get_balances(self) -> Dict[str, float]:
        """Return wallet balances. Placeholder for integration with on-chain calls."""

        # This should be implemented with web3 calls in live mode.
        return {"USDC": 0.0}

    def place_order(self, market_id: str, outcome_id: str, side: str, price: float, size: float, mode: str) -> Dict[str, str]:
        """Place an order on the CLOB (live) or simulate in paper mode."""

        if mode == "paper":
            logger.info("[PAPER] Simulated order %s %s @ %s size %s", side, outcome_id, price, size)
            return {"status": "filled", "order_id": "paper-simulated"}

        order_payload = {
            "market": market_id,
            "outcome": outcome_id,
            "side": side.lower(),
            "price": price,
            "size": size,
        }
        url = f"{self.clob_api_url}/orders"
        response = self._request_with_retry("POST", url, json=order_payload)
        return response.json()

    def get_order_status(self, order_id: str) -> Dict[str, str]:
        """Fetch order status from CLOB."""

        url = f"{self.clob_api_url}/orders/{order_id}"
        response = self._request_with_retry("GET", url)
        return response.json()


def _safe_float(value: Optional[float]) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_best_levels(outcome: Dict, order_book: Dict) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Derive best bid/ask and size from various order book shapes."""

    best_bid = _safe_float(order_book.get("bestBid") or outcome.get("bestBid"))
    best_ask = _safe_float(order_book.get("bestAsk") or outcome.get("bestAsk"))
    best_ask_size = _safe_float(order_book.get("bestAskSize") or outcome.get("bestAskSize"))

    asks = order_book.get("asks") or outcome.get("asks")
    if (best_ask is None or best_ask_size is None) and isinstance(asks, list) and asks:
        # Some responses only include raw ask levels; take the best one.
        top_ask = min(asks, key=lambda level: float(level.get("price", float("inf"))))
        best_ask = _safe_float(best_ask or top_ask.get("price"))
        best_ask_size = _safe_float(best_ask_size or top_ask.get("size") or top_ask.get("amount"))

    return best_bid, best_ask, best_ask_size


def _pick_end_date(item: Dict) -> str:
    """Choose the most likely end/resolve date field from a market payload."""

    for key in [
        "endDate",
        "resolveDate",
        "end_date",
        "resolve_time",
        "resolveTime",
        "closeDate",
        "expiry",
        "endTime",
        "resolutionTime",
    ]:
        if key in item and item[key]:
            return item[key]
    return ""
