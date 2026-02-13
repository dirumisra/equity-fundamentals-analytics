"""
N1–N4 — Null / Missing Value Validation

Validates:
N1: Identifier columns have 0 missing
N2: Core numeric columns have acceptable missing ratio (configurable)
N3: Feature columns (buckets/flags) have no missing where expected
N4: Screening pass flags have no missing (screen outputs)
"""

import pytest


# Fixtures must exist in conftest.py
ALL_DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

FEATURE_AND_SCREEN_DATASETS = [
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

SCREEN_ONLY_DATASETS = [
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]


# -------------------------
# CONFIG (industry-friendly defaults)
# -------------------------

ID_COLS = ["s_no", "company_name", "industry"]

CORE_NUMERIC_COLS = [
    "cmp_rs",
    "market_cap_cr",
    "debt_to_eq",
    "sales_cr",
    "sales_qtr_cr",
    "roe_pct",
    "roce_pct",
    "opm_pct",
    "sales_growth_pct",
    "profit_growth_pct",
    "profit_var_5yrs_pct",
    "eps_12m_rs",
    "peg",
    "pe",
    "pat_12m_cr",
    "cmp_to_bv",
]

# Max allowed missing ratio for numeric columns (per column)
# Keep it lenient for public market datasets (some fields legitimately missing)
MAX_NUMERIC_MISSING_RATIO = 0.30  # 30%
MAX_MISSING_RATIO_BY_COL = {
    "profit_var_5yrs_pct": 0.35,   # 5Y metric often missing; allow a bit more
}

# -------------------------
# HELPERS
# -------------------------

def assert_no_nulls(df, cols: list[str], dataset_label: str) -> None:
    missing_cols = [c for c in cols if c not in df.columns]
    assert not missing_cols, f"{dataset_label}: missing columns for null-check: {missing_cols}"

    null_counts = df[cols].isna().sum()
    bad = null_counts[null_counts > 0]
    assert bad.empty, f"{dataset_label}: nulls found in required columns: {bad.to_dict()}"


def assert_missing_ratio_ok(df, col: str, dataset_label: str, max_ratio: float) -> None:
    assert col in df.columns, f"{dataset_label}: missing column: {col}"
    total = len(df)
    if total == 0:
        pytest.fail(f"{dataset_label}: dataset is empty")

    nulls = df[col].isna().sum()
    ratio = nulls / total

    assert ratio <= max_ratio, (
        f"{dataset_label}: {col} missing ratio too high "
        f"({ratio:.2%} > {max_ratio:.2%}). Nulls={nulls}, Rows={total}"
    )


# -------------------------
# TESTS
# -------------------------

# N1: Identifier columns must never be missing
@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_nulls_n1_identifiers_not_null(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    assert_no_nulls(df, ID_COLS, dataset_label)


# N2: Numeric columns can be missing, but not beyond threshold
@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_nulls_n2_numeric_missing_ratio_ok(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    for c in CORE_NUMERIC_COLS:
        max_ratio = MAX_MISSING_RATIO_BY_COL.get(c, MAX_NUMERIC_MISSING_RATIO)
        assert_missing_ratio_ok(df, c, dataset_label, max_ratio)

# N3: Feature engineered buckets/flags should be present in feature/screen datasets
FEATURE_REQUIRED_COLS = [
    "is_valuation_known",
    "valuation_bucket",
    "is_profitable",
    "profitability_bucket",
    "capital_efficiency_flag",
    "is_growth_company",
    "growth_bucket",
]

@pytest.mark.parametrize("fixture_name,dataset_label", FEATURE_AND_SCREEN_DATASETS)
def test_nulls_n3_feature_columns_not_null(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    assert_no_nulls(df, FEATURE_REQUIRED_COLS, dataset_label)


# N4: Screening pass flags should never be null in screening outputs
SCREEN_FLAG_COLS = ["is_basic_screen_pass", "is_quality_screen_pass", "is_growth_screen_pass"]

@pytest.mark.parametrize("fixture_name,dataset_label", SCREEN_ONLY_DATASETS)
def test_nulls_n4_screen_flags_not_null(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    assert_no_nulls(df, SCREEN_FLAG_COLS, dataset_label)