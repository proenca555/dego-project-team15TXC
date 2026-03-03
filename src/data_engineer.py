from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


# -------------------------
# Paths / config
# -------------------------

@dataclass(frozen=True)
class PipelinePaths:
    repo_root: Path
    raw_json: Path
    curated_csv: Path
    dq_summary_csv: Path


def get_paths(repo_root: str | Path) -> PipelinePaths:
    repo_root = Path(repo_root).resolve()
    return PipelinePaths(
        repo_root=repo_root,
        raw_json=repo_root / "data" / "raw" / "raw_credit_applications.json",
        curated_csv=repo_root / "data" / "curated" / "credit_applications_curated.csv",
        dq_summary_csv=repo_root / "data" / "artifacts" / "data_quality_summary.csv",
    )


# -------------------------
# Loading / flattening
# -------------------------

def load_raw_records(raw_json_path: Path) -> list[dict]:
    with open(raw_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_records(records: list[dict]) -> pd.DataFrame:
    df = pd.json_normalize(records)

    # Ensure these exist (some records may be missing them)
    if "_id" not in df.columns:
        df["_id"] = pd.NA
    if "spending_behavior" not in df.columns:
        df["spending_behavior"] = pd.NA

    return df


# -------------------------
# Cleaning helpers
# -------------------------

_GENDER_MAP = {
    "M": "Male",
    "MALE": "Male",
    "F": "Female",
    "FEMALE": "Female",
}


def standardize_gender(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.upper()
    out = s.map(_GENDER_MAP).fillna("Unknown")
    out = out.replace({"": "Unknown", "NAN": "Unknown", "NONE": "Unknown"})
    return out


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """
    Handles mixed date formats:
      - YYYY-MM-DD
      - DD/MM/YYYY
      - YYYY/MM/DD
      - MM/DD/YYYY (ambiguous; best-effort parsing)
    """
    dt1 = pd.to_datetime(series, errors="coerce", dayfirst=True)
    mask = dt1.isna()
    if mask.any():
        dt2 = pd.to_datetime(series[mask], errors="coerce", dayfirst=False)
        dt1.loc[mask] = dt2
    return dt1


def unify_income(df: pd.DataFrame) -> pd.Series:
    """
    Some records use:
      - financials.annual_income
      - financials.annual_salary
    Also annual_income may be a string.
    """
    inc = df["financials.annual_income"] if "financials.annual_income" in df.columns else pd.Series(pd.NA, index=df.index)
    sal = df["financials.annual_salary"] if "financials.annual_salary" in df.columns else pd.Series(pd.NA, index=df.index)

    merged = inc.copy()
    merged = merged.where(~merged.isna(), sal)
    merged = pd.to_numeric(merged, errors="coerce")
    return merged


def extract_spending_features(spending_series: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    """
    spending_behavior is a list of {category, amount}.
    Produces:
      - one numeric column per category (amount)
      - total_spend_monthly
    """
    def to_dict(x: Any) -> Dict[str, float]:
        if isinstance(x, list):
            out: Dict[str, float] = {}
            for item in x:
                if not isinstance(item, dict):
                    continue
                cat = str(item.get("category", "")).strip()
                amt = item.get("amount", np.nan)
                if not cat:
                    continue
                try:
                    amt_f = float(amt)
                except Exception:
                    amt_f = np.nan
                out[cat] = amt_f
            return out
        return {}

    spending_dicts = spending_series.apply(to_dict)
    spending_df = spending_dicts.apply(pd.Series)

    if spending_df.shape[1] == 0:
        spending_df = pd.DataFrame(index=spending_series.index)

    for c in spending_df.columns:
        spending_df[c] = pd.to_numeric(spending_df[c], errors="coerce")

    total = spending_df.sum(axis=1, skipna=True)
    return spending_df, total


def drop_direct_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove direct identifiers from curated outputs:
      - full_name, email, ssn, ip_address
    """
    pii_cols = [
        "applicant_info.full_name",
        "applicant_info.email",
        "applicant_info.ssn",
        "applicant_info.ip_address",
    ]
    return df.drop(columns=[c for c in pii_cols if c in df.columns], errors="ignore")


# -------------------------
# Data Quality summary
# -------------------------

def make_dq_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing_n": [int(df[c].isna().sum()) for c in df.columns],
        "missing_pct": [float(df[c].isna().mean() * 100) for c in df.columns],
        "n_unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    out = out.sort_values(["missing_pct", "column"], ascending=[False, True]).reset_index(drop=True)
    return out


# -------------------------
# Main build
# -------------------------

def build_curated(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Standardize core fields
    df["annual_income"] = unify_income(df)

    if "applicant_info.gender" in df.columns:
        df["gender"] = standardize_gender(df["applicant_info.gender"])
    else:
        df["gender"] = "Unknown"

    if "applicant_info.date_of_birth" in df.columns:
        df["date_of_birth"] = parse_mixed_dates(df["applicant_info.date_of_birth"])
        today = pd.Timestamp.today()
        df["age"] = ((today - df["date_of_birth"]).dt.days / 365.25).floordiv(1)
        df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")
    else:
        df["date_of_birth"] = pd.NaT
        df["age"] = np.nan

    # Spending behavior → features
    spending_df, total_spend = extract_spending_features(
        df["spending_behavior"] if "spending_behavior" in df.columns else pd.Series([None] * len(df))
    )
    spending_df = spending_df.fillna(0)
    df = pd.concat([df.drop(columns=["spending_behavior"], errors="ignore"), spending_df], axis=1)
    df["total_spend_monthly"] = total_spend

    # Target + decision numeric fields
    if "decision.loan_approved" in df.columns:
        df["loan_approved"] = df["decision.loan_approved"].astype("boolean").astype("Int64")
    else:
        df["loan_approved"] = pd.Series([pd.NA] * len(df), dtype="Int64")

    for col in ["decision.interest_rate", "decision.approved_amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop redundant raw columns now that we have standardized ones
    redundant = [
        "financials.annual_income",
        "financials.annual_salary",
        "applicant_info.gender",
        "applicant_info.date_of_birth",
    ]
    df = df.drop(columns=[c for c in redundant if c in df.columns], errors="ignore")

    # Remove direct PII for curated dataset
    df = drop_direct_pii(df)

    # Drop redundant column of loan decision (loan_approved is the cleaned version)
    df = df.drop(columns=["decision.loan_approved"], errors="ignore")

    # Remove flagged duplicate and resubmission
    if "notes" in df.columns:
        mask_duplicates = (
            (df["notes"] == "DUPLICATE_ENTRY_ERROR") |
            (df["notes"] == "RESUBMISSION")
        )   
    
    df = df[~mask_duplicates].copy()

    return df


def run(repo_root: str | Path = ".") -> None:
    paths = get_paths(repo_root)

    # Ensure folders exist
    paths.curated_csv.parent.mkdir(parents=True, exist_ok=True)
    paths.dq_summary_csv.parent.mkdir(parents=True, exist_ok=True)

    # Load
    records = load_raw_records(paths.raw_json)
    df_raw = flatten_records(records)

    # Curate
    df_curated = build_curated(df_raw)

    # Save output
    df_curated.to_csv(paths.curated_csv, index=False)

    dq = make_dq_summary(df_curated)
    dq.to_csv(paths.dq_summary_csv, index=False)

    print("Data engineering pipeline complete.")
    print(f"Raw JSON:     {paths.raw_json}")
    print(f"Curated CSV:  {paths.curated_csv}")
    print(f"DQ summary:   {paths.dq_summary_csv}")


if __name__ == "__main__":
    run(".")