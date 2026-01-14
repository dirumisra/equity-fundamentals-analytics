# src/equity_analytics/io.py
# Centralized IO helpers for notebooks & pipelines

# src/equity_analytics/io.py
# Centralized IO helpers for notebooks & pipelines

from __future__ import annotations

from pathlib import Path
import pandas as pd

DEFAULT_PROCESSED_DIR = Path("data") / "processed"
DEFAULT_STD_FILENAME = "equity_df_std.csv"


def ensure_dir(path: Path) -> None:
    """Create parent directory if it doesn't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def save_equity_df_std(
    df: pd.DataFrame,
    processed_dir: Path | str = DEFAULT_PROCESSED_DIR,
    filename: str = DEFAULT_STD_FILENAME,
) -> Path:
    """
    Save the cleaned & standardized dataset to disk.
    Returns the saved file path.
    """
    processed_dir = Path(processed_dir)
    out_path = processed_dir / filename
    ensure_dir(out_path)

    df.to_csv(out_path, index=False)
    return out_path


def load_equity_df_std(
    processed_dir: Path | str = DEFAULT_PROCESSED_DIR,
    filename: str = DEFAULT_STD_FILENAME,
) -> pd.DataFrame:
    """
    Load the cleaned & standardized dataset from disk.
    """
    processed_dir = Path(processed_dir)
    in_path = processed_dir / filename

    if not in_path.exists():
        raise FileNotFoundError(
            f"Input not found: {in_path}. "
            f"Run the save step from the data intake notebook first."
        )

    return pd.read_csv(in_path)