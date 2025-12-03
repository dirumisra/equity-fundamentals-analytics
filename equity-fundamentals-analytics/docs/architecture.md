# Equity Fundamentals Analytics – System Architecture

## 1. Project Goal

Build an end-to-end equity fundamentals analytics pipeline that:

- Loads raw equity fundamentals data from CSV files  
- Cleans and standardizes the data into a consistent tabular format  
- Computes financial metrics and derived features  
- Applies screening and ranking logic to identify insights (value, quality, growth, etc.)  
- Runs in a configurable way across Dev, UAT, and Prod-like environments  

---

## 2. Architecture Layers

The project is organized into the following logical layers:

### Layer 1 – Data Intake Layer

**Purpose:**  
Read raw input data and perform basic exploration.

**Responsibilities:**

- Load raw CSV files from `data/raw/`  
- Basic structure checks (columns, row counts)  
- Simple exploratory analysis (head, info, describe)  
- Identify obvious data issues for the cleaning layer  

Artifacts:

- Notebooks in `notebooks/intake/`  
- Future Python code in `src/equity_analytics/intake.py`  

---

### Layer 2 – Data Cleaning & Standardization Layer

**Purpose:**  
Convert raw, inconsistent data into a clean and standardized dataset.

**Responsibilities:**

- Rename columns into a clear, consistent naming convention  
- Convert numeric columns (e.g. PE, ROE, ROCE, Debt/Equity) to proper numeric types  
- Handle missing or invalid values  
- Remove or flag obviously corrupted rows  
- Save cleaned data to `data/clean/`  

Artifacts:

- Notebooks in `notebooks/cleaning/`  
- Python code in `src/equity_analytics/cleaning.py`  

---

### Layer 3 – Feature Engineering & Financial Metrics Layer

**Purpose:**  
Add derived metrics and features that are useful for financial analysis.

**Responsibilities:**

- Compute derived ratios (e.g. computed PE, PEG) where possible  
- Add flags (e.g. low-debt, high-ROE)  
- Aggregate metrics at industry/sector level (e.g. sector average PE, ROE)  
- Create composite scores (e.g. quality score, value score, growth score)  
- Save feature-enriched data to `data/feature/`  

Artifacts:

- Notebooks in `notebooks/features/`  
- Python code in `src/equity_analytics/features.py`  

---

### Layer 4 – Screening, Ranking & Insights Layer

**Purpose:**  
Implement business logic for screening and ranking companies and generating insights.

**Responsibilities:**

- Implement reusable screening functions (e.g. value picks, quality picks, growth picks)  
- Implement ranking logic based on composite scores and metrics  
- Generate final insights tables (e.g. top N per industry, overall ranking)  
- Save final analytic outputs to `data/analytics/`  

Artifacts:

- Notebooks in `notebooks/analytics/`  
- Python code in `src/equity_analytics/analytics.py`  

---

### Layer 5 – Testing & Data Quality Layer

**Purpose:**  
Ensure the correctness and reliability of the pipeline.

**Responsibilities:**

- Unit tests for:
  - Data intake functions  
  - Cleaning functions  
  - Feature engineering functions  
  - Screening/ranking logic  
- Data quality checks on key columns and ranges  
- Simple end-to-end smoke test of the pipeline  

Artifacts:

- Test files in `tests/`  
- Optional data quality helpers in `src/equity_analytics/dq_tests.py`  

---

### Layer 6 – Documentation & Knowledge Layer

**Purpose:**  
Document the system so it can be understood, maintained, and extended.

**Responsibilities:**

- High-level architecture documentation (`docs/architecture.md`)  
- Workflow and process documentation (`docs/workflow.md`)  
- Financial metrics dictionary (`docs/metrics_dictionary.md`)  
- Project tracking overview (`docs/project_tracker.md`)  
- User/developer instructions in `README.md`  

---

### Layer 7 – Environment & Deployment Layer

**Purpose:**  
Simulate Dev, UAT, and Prod-like environments and make the pipeline configurable and runnable.

**Responsibilities:**

- Configuration files under `src/equity_analytics/config/` (e.g. dev/uat/prod)  
- Environment-specific settings (data paths, log levels, run modes)  
- Main pipeline runner (e.g. `src/equity_analytics/pipeline.py`)  
- Ability to run the pipeline in different modes (dev, uat, prod)  

Artifacts:

- Config files in `src/equity_analytics/config/`  
- Pipeline code in `src/equity_analytics/pipeline.py`  

---

## 3. High-Level Flow (Text Diagram)

```text
Raw Data (data/raw)
        │
        ▼
Data Intake (intake layer)
        │
        ▼
Cleaning & Standardization (cleaning layer)
        │
        ▼
Feature Engineering & Metrics (features layer)
        │
        ▼
Screening, Ranking & Insights (analytics layer)
        │
        ▼
Testing & Data Quality (tests + DQ checks)
        │
        ▼
Documentation (docs) + Environment & Deployment (Dev/UAT/Prod)