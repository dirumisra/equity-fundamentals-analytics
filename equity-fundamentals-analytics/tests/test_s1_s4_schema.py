"""
S1-S4 — Schema validation tests

Purpose:
---------
These tests validate the *schema only* (structure) of pipeline datasets.
They ensure:
- All required columns are present
- No duplicate column names exist

Important:
-----------
- These tests DO NOT validate data values or data quality.
- They strictly check column presence and uniqueness.
"""

import pytest

# -------------------------------------------------------------------
# DATASET FIXTURE REFERENCES
# -------------------------------------------------------------------
# These fixtures must be defined in `conftest.py`
# Format:
#   (fixture_name, expected_output_filename)
#
# Used only for documentation / clarity here.
DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]


# -------------------------------------------------------------------
# REQUIRED SCHEMA DEFINITIONS
# -------------------------------------------------------------------
# These constants define the *minimum required columns*
# for each stage of the pipeline.
#
# Each downstream dataset is expected to be a superset
# of the previous stage.

# Base standardized equity dataset columns
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

# Feature-enriched dataset columns
# Extends the standard dataset with derived signals
REQUIRED_FEATURE_COLUMNS = REQUIRED_STD_COLUMNS | {
    # valuation features
    "is_valuation_known",
    "valuation_bucket",

    # profitability & efficiency features
    "is_profitable",
    "profitability_bucket",
    "capital_efficiency_flag",

    # growth features
    "is_growth_company",
    "growth_bucket",
}

# Screened output dataset columns
# Adds pass/fail flags for different screening stages
REQUIRED_SCREEN_COLUMNS = REQUIRED_FEATURE_COLUMNS | {
    "is_basic_screen_pass",
    "is_quality_screen_pass",
    "is_growth_screen_pass",
}


# -------------------------------------------------------------------
# HELPER ASSERTION FUNCTIONS
# -------------------------------------------------------------------
# These helper functions keep test cases clean and readable.

def assert_no_duplicate_columns(df, dataset_label: str) -> None:
    """
    Assert that the DataFrame contains no duplicate column names.

    Args:
        df: pandas DataFrame under test
        dataset_label: filename or logical dataset name (used in error messages)
    """
    dupes = df.columns[df.columns.duplicated()].tolist()
    assert not dupes, f"{dataset_label}: duplicate column names found: {dupes}"


def assert_required_columns(df, required: set[str], dataset_label: str) -> None:
    """
    Assert that all required columns exist in the DataFrame.

    Args:
        df: pandas DataFrame under test
        required: set of required column names
        dataset_label: filename or logical dataset name (used in error messages)
    """
    missing = sorted(list(required - set(df.columns)))
    assert not missing, f"{dataset_label}: missing required columns: {missing}"


# -------------------------------------------------------------------
# TEST CASES
# -------------------------------------------------------------------

def test_schema_s1_equity_df_std(equity_df_std):
    """
    S1:
    Validate schema for the base standardized equity dataset.
    """
    assert_no_duplicate_columns(equity_df_std, "equity_df_std.csv")
    assert_required_columns(
        equity_df_std,
        REQUIRED_STD_COLUMNS,
        "equity_df_std.csv"
    )

def test_schema_s2_equity_features(equity_features_df):
    """
    S2:
    Validate schema for the feature-engineered equity dataset.
    """
    assert_no_duplicate_columns(equity_features_df, "equity_features_df.csv")
    assert_required_columns(
        equity_features_df,
        REQUIRED_FEATURE_COLUMNS,
        "equity_features_df.csv"
    )


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
    """
    S3:
    Validate schema for all screening output datasets.

    Uses pytest parameterization to avoid repetitive test code.
    """
    df = request.getfixturevalue(fixture_name)
    assert_no_duplicate_columns(df, dataset_label)
    assert_required_columns(
        df,
        REQUIRED_SCREEN_COLUMNS,
        dataset_label
    )
