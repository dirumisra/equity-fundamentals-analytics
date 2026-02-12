"""
R5 — Allowed categories validation (Bucket values)

Purpose:
- Ensure bucket columns only contain expected categorical values
- Ignore NULLs (handled in N-tests)
- Applies only to datasets where these columns exist (features + screened outputs)
"""

import pytest

# ------------------------------------------------------------
# Datasets that MUST contain bucket columns
# ------------------------------------------------------------
DATASETS_WITH_BUCKETS = [
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

# ------------------------------------------------------------
# Allowed sets (confirmed from your debug output)
# ------------------------------------------------------------
ALLOWED_VALUATION_BUCKETS = {"cheap", "fair", "expensive", "unknown"}
ALLOWED_PROFIT_BUCKETS = {"weak", "moderate", "strong"}
ALLOWED_GROWTH_BUCKETS = {"weak", "moderate", "strong"}


def assert_allowed_values(df, col: str, allowed: set[str], dataset_label: str) -> None:
    """Assert non-null unique values are a subset of allowed."""
    assert col in df.columns, f"{dataset_label}: missing required column '{col}'"

    observed = set(df[col].dropna().unique())
    unexpected = observed - allowed

    assert not unexpected, (
        f"{dataset_label}: unexpected values in '{col}': {sorted(unexpected)} "
        f"(allowed={sorted(allowed)})"
    )


@pytest.mark.parametrize("fixture_name,dataset_label", DATASETS_WITH_BUCKETS)
def test_r5_allowed_bucket_values(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)

    assert_allowed_values(df, "valuation_bucket", ALLOWED_VALUATION_BUCKETS, dataset_label)
    assert_allowed_values(df, "profitability_bucket", ALLOWED_PROFIT_BUCKETS, dataset_label)
    assert_allowed_values(df, "growth_bucket", ALLOWED_GROWTH_BUCKETS, dataset_label)