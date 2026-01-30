"""
Shared pytest configuration for Equity Fundamentals Analytics.

- Centralizes dataset loading for DEV environment
- Provides session-scoped fixtures used across all test modules
- Keeps individual test files small and focused
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

# -------------------------------------------
# Project paths (DEV)
# -------------------------------------------

# Resolve project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Directory containing processed DEV datasets
PROCESSED_DIR = PROJECT_ROOT / "notebooks" / "dev" / "data" / "processed"


def load_csv(filename: str) -> pd.DataFrame:
    """Load a processed CSV and fail fast if it is missing."""
    path = PROCESSED_DIR / filename
    if not path.exists():
        pytest.fail(f"Required file not found: {path}")
    return pd.read_csv(path)

# -------------------------------------------
# Fixtures (session scope)
# -------------------------------------------

@pytest.fixture(scope="session")
def equity_df_std():
    """Base standardized equity fundamentals dataset."""
    return load_csv("equity_df_std.csv")

@pytest.fixture(scope="session")
def equity_features_df():
    """Feature-engineered equity dataset for analytics and model tests."""
    return load_csv("equity_features_df.csv")

@pytest.fixture(scope="session")
def equity_screened_full():
    """Final equity universe after all screening rules are applied."""
    return load_csv("equity_screened_full.csv")

@pytest.fixture(scope="session")
def equity_basic_screen():
    """Equities passing basic eligibility screening."""
    return load_csv("equity_basic_screen.csv")

@pytest.fixture(scope="session")
def equity_quality_screen():
    """Equities passing quality-based screening criteria."""
    return load_csv("equity_quality_screen.csv")

@pytest.fixture(scope="session")
def equity_growth_screen():
    """Equities passing growth-based screening criteria."""
    return load_csv("equity_growth_screen.csv")
