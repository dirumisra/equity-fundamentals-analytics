"""
tests/test_r4_ratio_bounds.py

R4 — Ratio bounds validation

Purpose:
- Catch corrupted or extreme ratio values (PE/PEG/PB/Debt-to-Equity)
- Allow real-world negatives for PE/PEG (loss-making / negative growth)
- Ignore NULLs (handled in N-tests)
- Use HARD sanity caps with tiny tolerance for edge anomalies
"""

import pytest
import pandas as pd

# ------------------------------------------------------------
# Datasets (fixture_name, label)
# ------------------------------------------------------------
ALL_DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

# ------------------------------------------------------------
# Soft bounds (business sanity, allow some outliers)
# These are "reasonable" for screening / analytics, not mathematical limits.
# ------------------------------------------------------------
RATIO_BOUNDS = {
    "pe": (-200, 1000),        # allow negative PE, cap typical sanity
    "peg": (-50, 50),          # allow negative PEG, but keep sane
    "cmp_to_bv": (0, 50),      # PB shouldn't be negative; 0–50 is broad
    "debt_to_eq": (0, 20),     # very high leverage allowed, but not insane
}

# ------------------------------------------------------------
# Hard caps (corruption guardrails)
# If values exceed these, likely parsing/data corruption
# ------------------------------------------------------------
HARD_CAPS = {
    "pe": (-10_000, 10_000),
    "peg": (-1_000, 1_000),
    "cmp_to_bv": (0, 500),
    "debt_to_eq": (0, 200),
}

# ------------------------------------------------------------
# Tolerances
# ------------------------------------------------------------
SOFT_BAD_RATIO_DEFAULT = 0.02  # 2% allowed outside soft bounds

# (dataset_label, column) -> allowed outlier ratio
SOFT_BAD_RATIO_OVERRIDES = {
    # Growth screen may have more noisy PEG / PE extremes
    ("equity_growth_screen.csv", "peg"): 0.10,
    ("equity_growth_screen.csv", "pe"): 0.05,

    # Base / features can also have some weird PE/PEG tails
    ("equity_df_std.csv", "pe"): 0.05,
    ("equity_features_df.csv", "pe"): 0.05,
    ("equity_screened_full.csv", "pe"): 0.05,
}

HARD_BAD_RATIO_THRESHOLD = 0.005  # 0.5%
HARD_BAD_COUNT_THRESHOLD = 10     # OR at most 10 rows

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _get_sample(df: pd.DataFrame, idx, col: str, sample_n: int = 10) -> str:
    if len(idx) == 0:
        return ""
    if "company_name" in df.columns:
        out = df.loc[idx, ["company_name", col]].copy()
        out = out.sort_values(by=col, ascending=False)
    else:
        out = df.loc[idx, [col]].copy()
        out = out.sort_values(by=col, ascending=False)
    return out.head(sample_n).to_string(index=False)


def _series_nonnull(df: pd.DataFrame, col: str) -> pd.Series:
    s = df[col]
    return s.dropna()


def assert_hard_caps(
    df: pd.DataFrame,
    col: str,
    low: float,
    high: float,
    dataset_label: str,
    *,
    sample_n: int = 10,
) -> None:
    """Hard caps: protect against corrupted/extreme values, with tiny tolerance."""
    if col not in df.columns:
        return

    s = _series_nonnull(df, col)
    total = len(s)
    if total == 0:
        return

    bad_mask = (s < low) | (s > high)
    bad_count = int(bad_mask.sum())
    if bad_count == 0:
        return

    bad_ratio = bad_count / total

    if bad_ratio <= HARD_BAD_RATIO_THRESHOLD or bad_count <= HARD_BAD_COUNT_THRESHOLD:
        sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
        print(
            f"\n[WARN-HARD] {dataset_label}: {col} exceeded HARD cap [{low}, {high}] "
            f"| bad={bad_count}/{total} ({bad_ratio:.2%}) "
            f"(allowed up to {HARD_BAD_RATIO_THRESHOLD:.2%} or {HARD_BAD_COUNT_THRESHOLD} rows)\n"
            f"Sample offenders:\n{sample}\n"
        )
        return

    sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
    raise AssertionError(
        f"{dataset_label}: {col} FAILED HARD cap [{low}, {high}] "
        f"| bad={bad_count}/{total} ({bad_ratio:.2%}), "
        f"allowed={HARD_BAD_RATIO_THRESHOLD:.2%} or {HARD_BAD_COUNT_THRESHOLD} rows\n"
        f"Sample offenders:\n{sample}"
    )


def assert_soft_bounds(
    df: pd.DataFrame,
    col: str,
    low: float,
    high: float,
    dataset_label: str,
    *,
    max_bad_ratio: float = SOFT_BAD_RATIO_DEFAULT,
    sample_n: int = 10,
) -> None:
    """Soft bounds: allow a small % of outliers; fail if too many."""
    if col not in df.columns:
        return

    s = _series_nonnull(df, col)
    total = len(s)
    if total == 0:
        return

    bad_mask = (s < low) | (s > high)
    bad_count = int(bad_mask.sum())
    if bad_count == 0:
        return

    bad_ratio = bad_count / total
    effective_max_ratio = SOFT_BAD_RATIO_OVERRIDES.get((dataset_label, col), max_bad_ratio)

    if bad_ratio <= effective_max_ratio:
        sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
        print(
            f"\n[WARN-SOFT] {dataset_label}: {col} outside soft bounds [{low}, {high}] "
            f"| bad={bad_count}/{total} ({bad_ratio:.2%}), allowed={effective_max_ratio:.2%}\n"
            f"Sample offenders:\n{sample}\n"
        )
        return

    sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
    raise AssertionError(
        f"{dataset_label}: {col} out of soft bounds [{low}, {high}] "
        f"| bad={bad_count}/{total} ({bad_ratio:.2%}), allowed={effective_max_ratio:.2%}\n"
        f"Sample offenders:\n{sample}"
    )

# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_r4_ratio_bounds(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)

    # 1) Hard caps first
    for col, (low, high) in HARD_CAPS.items():
        assert_hard_caps(df, col, low, high, dataset_label)

    # 2) Soft bounds next
    for col, (low, high) in RATIO_BOUNDS.items():
        assert_soft_bounds(df, col, low, high, dataset_label)