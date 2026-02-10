import pandas as pd
import pytest

# List of all datasets to test, each represented as a tuple of dataset variable name and its corresponding CSV file
ALL_DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

# List of core numeric columns that are expected to be present in all datasets
CORE_NUMERIC_COLS = [
    "cmp_rs",
    "market_cap_cr",
    "debt_to_eq",
    "sales_cr",
    "sales_qtr_cr",
    "sales_growth_pct",
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
]

# Allowable maximum percentage of "dirty" or non-numeric values (1% tolerance)
MAX_BAD_RATIO = 0.01  # 1% of the values can be non-numeric after coercion


# Function to test if a column is numeric or can be coerced to numeric
def assert_numeric_or_coercible(df: pd.DataFrame, col: str, dataset_label: str) -> None:
    # Ensure the column exists in the dataset
    assert col in df.columns, f"{dataset_label}: missing column: {col}"

    s = df[col]  # Get the column's data series

    # Check if the column is already numeric, no action needed if it is
    if pd.api.types.is_numeric_dtype(s):
        return

    # Try coercing the column to numeric (any non-numeric strings become NaN)
    coerced = pd.to_numeric(s, errors="coerce")

    # Count how many NaNs were introduced by coercion (excluding original NaNs)
    orig_na = s.isna().sum()  # Count of NaNs in the original column
    new_na = coerced.isna().sum()  # Count of NaNs after coercion
    introduced = max(new_na - orig_na, 0)  # NaNs introduced by coercion

    # Count of non-null values in the original column (ignoring original NaNs)
    non_null = max(len(s) - orig_na, 1)

    # Calculate the ratio of non-numeric values (bad data) in the column
    bad_ratio = introduced / non_null

    # Assert that the bad ratio is below the acceptable threshold (1% by default)
    assert bad_ratio <= MAX_BAD_RATIO, (
        f"{dataset_label}: '{col}' not numeric enough. "
        f"Introduced_NaNs={introduced} of NonNull={non_null} (ratio={bad_ratio:.2%})"
    )


# Parametrized test function that runs the above check on each dataset and column
@pytest.mark.parametrize("fixture_name,dataset_label", ALL_DATASETS)
def test_r2_core_numeric_columns_numeric_or_coercible(request, fixture_name, dataset_label):
    # Get the dataset for testing by using the fixture
    df = request.getfixturevalue(fixture_name)

    # Run the numeric check for each of the core numeric columns
    for col in CORE_NUMERIC_COLS:
        # Call the function to verify the column is numeric or coercible to numeric
        assert_numeric_or_coercible(df, col, dataset_label)