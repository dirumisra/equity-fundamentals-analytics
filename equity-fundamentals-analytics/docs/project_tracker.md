# Project Tracking – EPIC Overview

This document defines the high-level EPICs for the **Equity Fundamentals Analytics** project.  
Each EPIC represents a major body of work that will be broken down into smaller tasks/issues.

---

## EPIC 0 – Project Setup & Repository Initialization

**Goal:**  
Bootstrap the project so that development can start on a solid, consistent foundation.

**Includes:**

- Creating the project folder structure  
- Initializing Git repository and remote (GitHub)  
- Setting up the Python virtual environment  
- Adding base files: `.gitignore`, `requirements.txt`, `LICENSE`, `README.md`  
- Verifying that the project opens correctly in VS Code  

---

## EPIC 1 – Data Intake & Profiling

**Goal:**  
Understand the raw equity dataset and its structure before any transformation.

**Includes:**

- Loading raw CSV files from `data/raw/`  
- Performing basic exploratory data analysis (EDA)  
- Reviewing columns, data types, row counts, and missing values  
- Identifying obvious anomalies and data issues  
- Summarizing key findings about the dataset  

Artifacts:

- Notebooks under `notebooks/intake/`  
- (Later) optional helper functions in `src/equity_analytics/intake.py`  

---

## EPIC 2 – Data Cleaning & Standardization

**Goal:**  
Transform the raw dataset into a clean, consistent, and analysis-ready format.

**Includes:**

- Renaming columns into a clear, consistent naming convention  
- Converting numeric columns from strings to proper numeric types  
- Handling missing or invalid values (e.g. "-", blanks)  
- Applying basic outlier rules where appropriate  
- Saving cleaned output to `data/clean/`  

Artifacts:

- Notebooks under `notebooks/cleaning/`  
- Core cleaning logic in `src/equity_analytics/cleaning.py`  

---

## EPIC 3 – Feature Engineering & Financial Metrics

**Goal:**  
Enrich the cleaned dataset with derived financial metrics and features.

**Includes:**

- Computing derived metrics (e.g. computed PE, PEG where possible)  
- Adding boolean flags (e.g. low-debt, high-ROE)  
- Creating sector/industry-level aggregates (e.g. average PE, ROE)  
- Designing composite scores (e.g. quality, value, growth scores)  
- Saving enriched datasets to `data/feature/`  

Artifacts:

- Notebooks under `notebooks/features/`  
- Feature engineering code in `src/equity_analytics/features.py`  

---

## EPIC 4 – Screening, Ranking & Insights

**Goal:**  
Implement the business logic layer that converts metrics into actionable insights.

**Includes:**

- Implementing reusable screening functions (e.g. value picks, quality picks)  
- Implementing ranking logic across companies and sectors  
- Generating final ranked and filtered tables  
- Producing outputs (e.g. CSVs/Parquets) under `data/analytics/`  

Artifacts:

- Notebooks under `notebooks/analytics/`  
- Screening and ranking logic in `src/equity_analytics/analytics.py`  

---

## EPIC 5 – Testing & Data Quality Validation

**Goal:**  
Ensure that the pipeline is correct, robust, and repeatable.

**Includes:**

- Writing unit tests for:
  - Cleaning functions  
  - Feature engineering functions  
  - Screening/ranking functions  
- Implementing data quality checks (DQC) for key metrics and ranges  
- Creating a simple end-to-end smoke test of the pipeline  

Artifacts:

- Test files in `tests/` (e.g. `test_cleaning.py`, `test_features.py`, `test_analytics.py`)  
- Optional helpers in `src/equity_analytics/dq_tests.py`  

---

## EPIC 6 – Documentation & Knowledge Artifacts

**Goal:**  
Document the system so it is understandable for future contributors and hiring managers.

**Includes:**

- Maintaining `README.md` with clear project overview and setup instructions  
- Updating `docs/architecture.md` (system design)  
- Maintaining `docs/workflow.md` (step-by-step process)  
- Maintaining `docs/metrics_dictionary.md` (finance metrics definitions)  
- Ensuring high-level project status is tracked here in `docs/project_tracker.md`  

---

## EPIC 7 – Environment & Deployment Simulation (Dev/UAT/Prod)

**Goal:**  
Simulate real-world Dev, UAT, and Prod behavior for the analytics pipeline.

**Includes:**

- Configuration files under `src/equity_analytics/config/` (dev/uat/prod)  
- Environment-specific settings (data paths, log levels, run modes)  
- Main pipeline runner (e.g. `src/equity_analytics/pipeline.py`)  
- Ability to execute the pipeline in different modes (dev, uat, prod)  
- (Optional) basic scheduling/deployment simulation for a “production-like” feel  

---

## Status

- EPIC definitions: ✔ Finalized  
- Next step: Create issues/tasks mapped to these EPICs (later, via GitHub Project).