"""
tests/test_r3_percentage_bounds.py

R3 — Percentage bounds validation

Purpose:
- Catch corrupted or extreme percentage values
- Allow real-world negatives and high-growth outliers
- Ignore NULLs (handled in N-tests)
- Add HARD sanity caps with small tolerance for edge-denominator explosions
"""

"""
tests/test_r3_percentage_bounds.py

R3 — Percentage bounds validation

Purpose:
- Catch corrupted or extreme percentage values (e.g., from division by near-zero denominators)
- Allow real-world negatives and high-growth outliers (legitimate business scenarios)
- Ignore NULLs (these are handled separately in N-tests)
- Use two-tier validation: HARD caps (corruption guard) + SOFT bounds (business sanity)

Example Business Cases:
- A company with ₹1L profit last year and ₹20L this year = 1900% growth (legitimate)
- Operating margin can be negative (startup burning cash) or very high (software company)
- Small revenue bases can cause percentage explosions (₹1000 → ₹100,000 sales = 9900% growth)
"""

import pytest
import pandas as pd

# ------------------------------------------------------------
# Datasets (fixture_name, label)
# ------------------------------------------------------------
ALL_DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),              # Standard equity data (3145 companies)
    ("equity_features_df", "equity_features_df.csv"),    # With engineered features
    ("equity_screened_full", "equity_screened_full.csv"), # All screening flags
    ("equity_basic_screen", "equity_basic_screen.csv"),  # Basic quality filter (~821 companies)
    ("equity_quality_screen", "equity_quality_screen.csv"), # Quality + profitability (~230 companies)
    ("equity_growth_screen", "equity_growth_screen.csv"), # High-growth companies (~416 companies)
]

# ------------------------------------------------------------
# Soft bounds (business sanity, but not "hard corruption")
# These represent reasonable business ranges but allow outliers
# ------------------------------------------------------------
PCT_BOUNDS = {
    # Return metrics: can be negative (losses) or very high (exceptional performance)
    "roe_pct": (-500, 500),      # Return on Equity: -500% to 500%
    "roce_pct": (-500, 500),     # Return on Capital Employed: -500% to 500%
    "opm_pct": (-500, 500),      # Operating Profit Margin: -500% to 500%
    
    # Growth metrics: wider ranges to accommodate startups and turnarounds
    "sales_growth_pct": (-100, 500),      # Revenue can shrink 100% (→0) or grow 500% (6x)
    "profit_growth_pct": (-100, 2000),    # Profit highly volatile: can grow 20x year-over-year
    "profit_var_5yrs_pct": (-100, 300),   # 5-year profit variance
}

# ------------------------------------------------------------
# Hard caps (corruption guardrails; still allow tiny outliers)
# These catch data corruption or calculation errors
# We allow a few violations (0.5% or 10 rows) for edge cases like:
# - Division by near-zero denominators
# - Companies with ₹1 equity showing extreme ROE
# ------------------------------------------------------------
HARD_CAPS = {
    # Return metrics: extreme caps to catch corruption
    "roe_pct": (-10000, 10000),          # ROE can explode if equity ~₹0
    "roce_pct": (-10000, 10000),         # ROCE can explode if capital ~₹0
    "opm_pct": (-10000, 100000),         # OPM can explode if sales ~₹0
    
    # Growth metrics: very wide caps for data integrity only
    "sales_growth_pct": (-5000, 50000),   # Catches data entry errors
    "profit_growth_pct": (-5000, 75000),  # Allows for extreme turnarounds
    "profit_var_5yrs_pct": (-5000, 50000),
}

# ------------------------------------------------------------
# Tolerances
# ------------------------------------------------------------
# Default: Allow 2% of rows to violate soft bounds
SOFT_BAD_RATIO_DEFAULT = 0.02  # 2%

# Dataset-specific overrides: Different datasets have different volatility profiles
SOFT_BAD_RATIO_OVERRIDES = {
    # Full datasets (3145 companies): High variance due to including penny stocks,
    # distressed companies, and startups with extreme metrics
    "equity_df_std.csv": 0.15,          # 15% - base dataset (profit growth very volatile)
    "equity_features_df.csv": 0.15,     # 15% - same data, different columns
    "equity_screened_full.csv": 0.15,   # 15% - same data with all screening flags
    
    # Screened datasets: Lower variance as weak companies are filtered out
    "equity_basic_screen.csv": 0.04,    # 4% - basic quality filter applied
    "equity_quality_screen.csv": 0.05,  # 5% - quality screen (still some outliers)
    "equity_growth_screen.csv": 0.15,   # 15% - growth stocks are inherently volatile
}

# Hard-cap tolerance: Allow tiny number of extreme outliers (corruption guard only)
HARD_BAD_RATIO_THRESHOLD = 0.005  # 0.5% of data
HARD_BAD_COUNT_THRESHOLD = 10     # OR at most 10 rows (whichever is more permissive)
# Example: In 3000 rows, allow max(15 rows from 0.5%, 10 rows) = 15 rows


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def _get_sample(df: pd.DataFrame, idx, col: str, sample_n: int = 10) -> str:
    """
    Get a sample of offending rows for debugging.
    
    Args:
        df: Full DataFrame
        idx: Index of rows that violated bounds
        col: Column name being tested
        sample_n: Number of sample rows to return
    
    Returns:
        Formatted string showing worst offenders (sorted by column value)
    """
    if len(idx) == 0:
        return ""
    
    # Include company name if available for better debugging
    if "company_name" in df.columns:
        out = df.loc[idx, ["company_name", col]].copy()
        out = out.sort_values(by=col, ascending=False)  # Highest values first
    else:
        out = df.loc[idx, [col]].copy()
        out = out.sort_values(by=col, ascending=False)
    
    return out.head(sample_n).to_string(index=False)


def assert_pct_bounds_soft(
    df: pd.DataFrame,
    col: str,
    low: float,
    high: float,
    dataset_label: str,
    *,
    allow_null: bool = True,
    max_bad_ratio: float = SOFT_BAD_RATIO_DEFAULT,
    sample_n: int = 10,
) -> None:
    """
    Soft bounds check: Business sanity, allows some outliers.
    
    Purpose: Ensure most values are within reasonable business ranges,
    but allow a small percentage of legitimate outliers (e.g., turnarounds,
    startups with extreme growth rates).
    
    Args:
        df: DataFrame to test
        col: Column name
        low, high: Acceptable range
        dataset_label: Name for error messages
        allow_null: If True, skip NULL values (handled in N-tests)
        max_bad_ratio: Maximum % of rows allowed outside bounds
        sample_n: Number of sample rows to show in warnings/errors
    
    Behavior:
        - If violations ≤ max_bad_ratio: Print warning, continue
        - If violations > max_bad_ratio: Raise AssertionError (test fails)
    """
    if col not in df.columns:
        return

    s = df[col]
    if allow_null:
        s = s.dropna()  # Exclude NULLs from validation

    total = len(s)
    if total == 0:
        return  # No data to validate

    # Identify rows outside bounds
    bad_mask = (s < low) | (s > high)
    bad_count = int(bad_mask.sum())
    if bad_count == 0:
        return  # All values within bounds ✓
    
    bad_ratio = bad_count / total
    
    # Use dataset-specific tolerance if available, else default
    effective_max_ratio = SOFT_BAD_RATIO_OVERRIDES.get(dataset_label, max_bad_ratio)
    
    if bad_ratio <= effective_max_ratio:
        # Acceptable number of outliers: WARN but don't fail
        sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
        print(
            f"\n[WARN-SOFT] {dataset_label}: {col} outside soft bounds [{low}, {high}] "
            f"| bad={bad_count}/{total} ({bad_ratio:.2%}), allowed={effective_max_ratio:.2%}\n"
            f"Sample offenders:\n{sample}\n"
        )
        return
    
    # Too many outliers: FAIL the test
    sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
    raise AssertionError(
        f"{dataset_label}: {col} out of soft bounds [{low}, {high}] "
        f"| bad={bad_count}/{total} ({bad_ratio:.2%}), allowed={effective_max_ratio:.2%}\n"
        f"Sample offenders:\n{sample}"
    )


def assert_hard_caps(
    df: pd.DataFrame,
    col: str,
    low: float,
    high: float,
    dataset_label: str,
    *,
    allow_null: bool = True,
    sample_n: int = 10,
) -> None:
    """
    Hard caps check: Corruption guard, very permissive.
    
    Purpose: Catch truly corrupted/impossible values while allowing
    extreme edge cases caused by:
    - Near-zero denominators (e.g., ₹1 equity → ROE of 50,000%)
    - Data entry errors (e.g., decimal point mistakes)
    - Penny stocks with extreme volatility
    
    These caps are intentionally wide. Only massive violations fail the test.
    
    Args:
        df: DataFrame to test
        col: Column name
        low, high: Corruption guard thresholds
        dataset_label: Name for error messages
        allow_null: If True, skip NULL values
        sample_n: Number of sample rows to show
    
    Behavior:
        - If violations ≤ 0.5% OR ≤ 10 rows: Print warning, continue
        - If violations > threshold: Raise AssertionError (likely data corruption)
    """
    if col not in df.columns:
        return

    s = df[col]
    if allow_null:
        s = s.dropna()

    total = len(s)
    if total == 0:
        return

    # Identify extreme outliers beyond hard caps
    bad_mask = (s < low) | (s > high)
    bad_count = int(bad_mask.sum())
    if bad_count == 0:
        return  # No extreme outliers ✓

    bad_ratio = bad_count / total

    # Allow tiny number of hard-cap violations (edge cases like denominator ~0)
    if bad_ratio <= HARD_BAD_RATIO_THRESHOLD or bad_count <= HARD_BAD_COUNT_THRESHOLD:
        # Within tolerance: WARN but don't fail
        sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
        print(
            f"\n[WARN-HARD] {dataset_label}: {col} exceeded HARD cap [{low}, {high}] "
            f"| bad={bad_count}/{total} ({bad_ratio:.2%}) "
            f"(allowed up to {HARD_BAD_RATIO_THRESHOLD:.2%} or {HARD_BAD_COUNT_THRESHOLD} rows)\n"
            f"Sample offenders:\n{sample}\n"
        )
        return

    # Too many extreme outliers: Likely data corruption, FAIL the test
    sample = _get_sample(df, s.index[bad_mask], col, sample_n=sample_n)
    raise AssertionError(
        f"{dataset_label}: {col} FAILED HARD sanity cap [{low}, {high}] "
        f"| bad={bad_count}/{total} ({bad_ratio:.2%}), "
        f"allowed={HARD_BAD_RATIO_THRESHOLD:.2%} or {HARD_BAD_COUNT_THRESHOLD} rows\n"
        f"Sample offenders:\n{sample}"
    )


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_r3_percentage_bounds(request, fixture_name, dataset_label):
    """
    Two-tier validation for percentage columns:
    
    1. HARD CAPS (corruption guard):
       - Very wide bounds to catch data errors
       - Allow 0.5% or 10 rows to violate (edge cases like denominator ~0)
       - Example: OPM between -10,000% and 100,000%
    
    2. SOFT BOUNDS (business sanity):
       - Reasonable business ranges
       - Allow dataset-specific % of outliers (2-15%)
       - Example: OPM between -500% and 500% with 15% outliers allowed
    
    Flow:
        Load dataset → Check hard caps → Check soft bounds → Pass/Fail
    
    Why two tiers?
        - Hard caps catch corruption without false positives
        - Soft bounds enforce business logic while allowing real outliers
        - Prevents test brittleness from legitimate edge cases
    """
    df = request.getfixturevalue(fixture_name)

    # 1) Hard caps first (corruption guard)
    # Fail only if massive number of rows have impossible values
    for col, (low, high) in HARD_CAPS.items():
        if col in df.columns:
            assert_hard_caps(df, col, low, high, dataset_label)

    # 2) Soft bounds next (business sanity; allow some outliers)
    # Fail if too many rows outside reasonable business ranges
    for col, (low, high) in PCT_BOUNDS.items():
        if col in df.columns:
            assert_pct_bounds_soft(df, col, low, high, dataset_label)