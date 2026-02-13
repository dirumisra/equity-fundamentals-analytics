"""
C1–C3 — Row count & fail-fast checks

Purpose:
- Ensure datasets are not empty
- Ensure screened datasets are subsets of upstream datasets
- Ensure the full screened universe is consistent with basic/quality/growth outputs
"""

import pytest

# ------------------------------------------------------------
# Datasets (fixture_name, label)
# ------------------------------------------------------------
DATASETS = [
    ("equity_df_std", "equity_df_std.csv"),
    ("equity_features_df", "equity_features_df.csv"),
    ("equity_screened_full", "equity_screened_full.csv"),
    ("equity_basic_screen", "equity_basic_screen.csv"),
    ("equity_quality_screen", "equity_quality_screen.csv"),
    ("equity_growth_screen", "equity_growth_screen.csv"),
]

# For subset checks we need a stable unique key
# (In your schema, company_name + industry is the safest available composite)
KEY_COLS = ["company_name", "industry"]


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def assert_non_empty(df, dataset_label: str) -> None:
    assert len(df) > 0, f"{dataset_label}: dataset is empty (0 rows)"


def assert_key_cols_exist(df, dataset_label: str) -> None:
    missing = [c for c in KEY_COLS if c not in df.columns]
    assert not missing, f"{dataset_label}: missing key columns for subset checks: {missing}"


def key_set(df):
    # dropna to avoid key corruption
    return set(tuple(x) for x in df[KEY_COLS].dropna().itertuples(index=False, name=None))


# ------------------------------------------------------------
# C1 — Fail-fast: dataset not empty
# ------------------------------------------------------------
@pytest.mark.parametrize("fixture_name,dataset_label", DATASETS)
def test_c1_dataset_not_empty(request, fixture_name, dataset_label):
    df = request.getfixturevalue(fixture_name)
    assert_non_empty(df, dataset_label)


# ------------------------------------------------------------
# C2 — Screened datasets must be subset of equity_features_df
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "fixture_name,dataset_label",
    [
        ("equity_screened_full", "equity_screened_full.csv"),
        ("equity_basic_screen", "equity_basic_screen.csv"),
        ("equity_quality_screen", "equity_quality_screen.csv"),
        ("equity_growth_screen", "equity_growth_screen.csv"),
    ],
)
def test_c2_screened_are_subsets_of_features(request, fixture_name, dataset_label, equity_features_df):
    df = request.getfixturevalue(fixture_name)

    assert_key_cols_exist(df, dataset_label)
    assert_key_cols_exist(equity_features_df, "equity_features_df.csv")

    features_keys = key_set(equity_features_df)
    screened_keys = key_set(df)

    # all screened keys must exist in features
    missing = screened_keys - features_keys
    assert not missing, (
        f"{dataset_label}: contains rows not found in equity_features_df.csv "
        f"(missing_keys_count={len(missing)})"
    )


# ------------------------------------------------------------
# C3 — equity_screened_full should match intersection of (basic ∩ quality ∩ growth)
# if your "screened_full" is designed as combined screen.
# ------------------------------------------------------------
def test_c3_screened_full_contains_all_screened_sets(
    equity_screened_full,
    equity_basic_screen,
    equity_quality_screen,
    equity_growth_screen,
):
    """
    equity_screened_full is the full universe with screening flags.
    So it must contain every record that appears in any of the screened datasets.
    """

    assert_key_cols_exist(equity_screened_full, "equity_screened_full.csv")
    assert_key_cols_exist(equity_basic_screen, "equity_basic_screen.csv")
    assert_key_cols_exist(equity_quality_screen, "equity_quality_screen.csv")
    assert_key_cols_exist(equity_growth_screen, "equity_growth_screen.csv")

    full_keys = key_set(equity_screened_full)
    basic_keys = key_set(equity_basic_screen)
    quality_keys = key_set(equity_quality_screen)
    growth_keys = key_set(equity_growth_screen)

    # Expect union of screened sets to be present in full universe
    union_screened = basic_keys | quality_keys | growth_keys

    missing = union_screened - full_keys

    assert not missing, (
        "equity_screened_full.csv must contain all keys from "
        "basic/quality/growth screened datasets (union check failed).\n"
        f"missing_count={len(missing)}"
    )