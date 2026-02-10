"""
R1 — Non-negative checks (strict)

Purpose:
- Catch truly invalid negatives (data corruption) early.
- Keep it realistic for equities: sales/profits/EPS can be negative in real life,
  so we do NOT enforce those here.

Datasets covered:
- equity_df_std
- equity_features_df
- equity_screened_full
- equity_basic_screen
- equity_quality_screen
- equity_growth_screen
"""

import pytest


ALL_DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

# These should never be negative (strict)
STRICT_NON_NEGATIVE = [
    "cmp_rs",         # market price cannot be negative
    "market_cap_cr",  # market cap cannot be negative
]


def assert_non_negative(df, col: str, dataset_label: str) -> None:
    assert col in df.columns, f"{dataset_label}: missing column: {col}"

    s = df[col].dropna()

    # if dataset has values, ensure all >= 0
    bad = (s < 0).sum()
    assert bad == 0, f"{dataset_label}: {col} has {bad} values < 0"


@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_r1_strict_non_negative(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    for col in STRICT_NON_NEGATIVE:
        assert_non_negative(df, col, dataset_label)
