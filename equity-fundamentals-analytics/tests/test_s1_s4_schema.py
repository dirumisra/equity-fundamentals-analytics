"""
S1–S4 — Schema validation

Validates:
- Required columns exist
- No duplicate column names
Across all pipeline datasets.

Note:
- This checks ONLY schema (column presence), not data quality.
"""

import pytest


# These fixtures must exist in conftest.py
DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]


# -------------------------
# REQUIRED SCHEMA DEFINITIONS
# -------------------------

REQUIRED_STD_COLUMNS = {
    "s_no",
    "industry",
    "company_name",
    "cmp_rs",
    "market_cap_cr",
    "debt_to_eq",
    "sales_cr",
    "sales_growth_pct",
    "sales_qtr_cr",
    "profit_growth_pct",
    "profit_var_5yrs_pct",
    "roe_pct",
    "opm_pct",
    "eps_12m_rs",
    "peg",
    "pe",
    "pat_12m_cr",
    "roce_pct",
    "cmp_to_bv",
}

REQUIRED_FEATURE_COLUMNS = REQUIRED_STD_COLUMNS | {
    # valuation
    "is_valuation_known",
    "valuation_bucket",
    # profitability/efficiency
    "is_profitable",
    "profitability_bucket",
    "capital_efficiency_flag",
    # growth
    "is_growth_company",
    "growth_bucket",
}

REQUIRED_SCREEN_COLUMNS = REQUIRED_FEATURE_COLUMNS | {
    "is_basic_screen_pass",
    "is_quality_screen_pass",
    "is_growth_screen_pass",
}


# -------------------------
# HELPERS
# -------------------------

def assert_no_duplicate_columns(df, dataset_label: str) -> None:
    dupes = df.columns[df.columns.duplicated()].tolist()
    assert not dupes, f"{dataset_label}: duplicate column names found: {dupes}"


def assert_required_columns(df, required: set[str], dataset_label: str) -> None:
    missing = sorted(list(required - set(df.columns)))
    assert not missing, f"{dataset_label}: missing required columns: {missing}"


# -------------------------
# TESTS
# -------------------------

def test_schema_s1_equity_df_std(equity_df_std):
    assert_no_duplicate_columns(equity_df_std, "equity_df_std.csv")
    assert_required_columns(equity_df_std, REQUIRED_STD_COLUMNS, "equity_df_std.csv")


def test_schema_s2_equity_features(equity_features_df):
    assert_no_duplicate_columns(equity_features_df, "equity_features_df.csv")
    assert_required_columns(equity_features_df, REQUIRED_FEATURE_COLUMNS, "equity_features_df.csv")


@pytest.mark.parametrize(
    "fixture_name,dataset_label",
    [
        ("equity_screened_full", "equity_screened_full.csv"),
        ("equity_basic_screen", "equity_basic_screen.csv"),
        ("equity_quality_screen", "equity_quality_screen.csv"),
        ("equity_growth_screen", "equity_growth_screen.csv"),
    ],
)
def test_schema_s3_screen_outputs(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    assert_no_duplicate_columns(df, dataset_label)
    assert_required_columns(df, REQUIRED_SCREEN_COLUMNS, dataset_label)
