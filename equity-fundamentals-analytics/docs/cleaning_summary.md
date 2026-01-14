## Data Cleaning & Standardization Summary (EPIC 2)

This project follows a business-aware and conservative data cleaning strategy suitable for financial and equity analysis. The objective is to preserve the original meaning of financial metrics while ensuring a clean, analysis-ready dataset.

### 1. Column Name Standardization
- All column names were standardized to `lowercase` and `snake_case`
- Units were preserved using clear suffixes:
  - `_rs` for Rupees
  - `_cr` for Crores
  - `_pct` for percentages
  - `_to_` for ratios
- Special characters, spaces, and hidden non-breaking spaces were removed
- A rename mapping was explicitly defined and reviewed before application

Result:
- Consistent, machine-friendly schema compatible with Python, SQL, dbt, and BI tools
- No data values were modified during this step

### 2. Missing Value Handling Strategy
Missing values were handled based on column category and business meaning:

**Identifier Columns**
- (`s_no`, `company_name`)
- Must never be null
- Validated to ensure zero missing values

**Categorical Columns**
- (`industry`)
- Missing values retained as `NaN`
- No forced labels such as "Unknown" applied at this stage

**Numeric Raw Columns**
- (`cmp_rs`, `market_cap_cr`, `sales_cr`, `sales_qtr_cr`, `pat_12m_cr`, `eps_12m_rs`)
- Represent absolute financial facts
- Missing values retained as `NaN`
- No mean/median imputation performed
- Intended to be handled via conditional filtering during analysis

**Derived / Ratio Columns**
- (`pe`, `peg`, `roe_pct`, `roce_pct`, `opm_pct`, growth and ratio metrics)
- Missing values are expected and meaningful
- Never imputed or coerced
- Missing indicates “not applicable” or “not computable”

### 3. Validation Checks
- Identifier integrity validated (no missing identifiers)
- Missing value baselines recorded after schema standardization
- No rows were dropped during cleaning
- Raw data preserved separately from cleaned dataset

Final cleaned dataset reference:
- `equity_df_std`