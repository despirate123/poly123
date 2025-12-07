"""Configuration utilities for the Polymarket bot."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import yaml

load_dotenv()


@dataclass
class TradingConfig:
    """Trading parameters and thresholds for the strategy."""

    max_balance_to_use: float = 30.0
    max_position_per_market: float = 5.0
    max_open_exposure: float = 15.0
    min_probability_price: float = 0.97
    max_probability_price: float = 0.995
    max_time_to_resolution_hours: float = 24.0
    min_liquidity: float = 1.0
    min_trade_size: float = 1.0
    scan_interval_seconds: int = 60


@dataclass
class AppConfig:
    """Top-level configuration for the bot."""

    private_key: Optional[str]
    rpc_url: str
    data_api_url: str
    clob_api_url: str
    mode: str = "paper"
    trading: TradingConfig = TradingConfig()

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        """Create configuration from a YAML or JSON file."""

        raw: Dict[str, Any]
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        if path.suffix.lower() == ".json":
            raw = json.loads(path.read_text())
        else:
            raw = yaml.safe_load(path.read_text()) or {}

        trading_raw = raw.get("trading", {})
        trading = TradingConfig(**trading_raw)

        return cls(
            private_key=os.getenv("PRIVATE_KEY"),
            rpc_url=os.getenv("RPC_URL", raw.get("rpc_url", "")),
            data_api_url=raw.get(
                "data_api_url",
                "https://clob.polymarket.com/markets?limit=100&offset=0",
            ),
            clob_api_url=raw.get("clob_api_url", "https://clob.polymarket.com"),
            mode=os.getenv("MODE", raw.get("mode", "paper")),
            trading=trading,
        )


DEFAULT_CONFIG_PATH = Path(os.getenv("CONFIG_FILE", "config.yaml"))


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    """Load configuration from file and environment variables."""

    if path.exists():
        return AppConfig.from_file(path)

    return AppConfig(
        private_key=os.getenv("PRIVATE_KEY"),
        rpc_url=os.getenv("RPC_URL", ""),
        data_api_url="https://clob.polymarket.com/markets?limit=100&offset=0",
        clob_api_url="https://clob.polymarket.com",
        mode=os.getenv("MODE", "paper"),
    )
