# GDPR Mapping and Data Governance Assessment

## 1. Project Purpose (Purpose Limitation – GDPR Art. 5)

The purpose of this project is to analyze a credit application dataset and investigate
data quality, potential bias, and fairness issues in loan approval decisions.

The analysis supports responsible data processing by ensuring that the dataset used
for modeling is reliable and does not introduce discriminatory outcomes.

Supporting analyses:
- [Data Quality Analysis](../notebooks/01-data-quality.ipynb)
- [Bias and Fairness Analysis](../notebooks/02-bias-analysis.ipynb)



## 2. Data Description

The dataset used in this project contains credit application records used to
evaluate loan approval outcomes.

Although the dataset represents credit applications, it does not contain
direct personal identifiers such as names, phone numbers, or email addresses.
However, some attributes such as age or geographic information may still act
as indirect identifiers and therefore require careful governance and fairness
evaluation.

### Personal Data Assessment

To evaluate potential privacy risks, the dataset was reviewed to identify
fields that may contain personal or indirectly identifiable information.

Direct identifiers such as names, email addresses, phone numbers, or
government identification numbers are not present in the dataset.

However, some attributes may still act as indirect identifiers,
including:

- Age
- Geographic information (ZIP code)
- Income-related attributes

While these fields do not directly identify individuals, combinations
of such attributes could potentially enable indirect identification.
Therefore, appropriate governance practices and fairness analysis are
necessary when using the dataset.

The raw dataset is processed through a data engineering pipeline that transforms the data from JSON format into a curated dataset used for analysis.

Dataset characteristics:
- 500 records
- 32 variables
- stored in [credit_applications_curated.csv](../data/curated/credit_applications_curated.csv)

The data engineering pipeline and dataset preparation process are documented in
[Data Quality Analysis](../notebooks/01-data-quality.ipynb).

## 3. Accuracy Principle (GDPR Art. 5(1)(d))

GDPR requires personal data to be accurate and kept up to date.

A comprehensive data quality assessment was conducted in
[Data Quality Analysis](../notebooks/01-data-quality.ipynb).

The analysis evaluated several dimensions of data quality:

- Completeness
- Consistency
- Validity
- Uniqueness
- Accuracy

Key findings include:

- One record with non-positive income
- One record with debt-to-income ratio outside the expected range
- No unrealistic age values detected

Problematic records were flagged for remediation before further analysis,
ensuring that the curated dataset meets acceptable data quality standards.

## 4. Fairness and Non-Discrimination (GDPR Art. 5 & Art. 22)

GDPR emphasizes fair processing and protection against discriminatory outcomes
resulting from automated decision systems.

To evaluate fairness risks, a bias and fairness analysis was conducted in
[Bias and Fairness Analysis](../notebooks/02-bias-analysis.ipynb).

The analysis included:

- Disparate Impact Ratio analysis for gender
- Age-based bias assessment
- Proxy discrimination analysis using geographic variables (ZIP code)
- Logistic regression modeling to evaluate relationships between demographic
  attributes and loan approval outcomes

These analyses help detect whether approval decisions differ significantly
across demographic groups and whether indirect discrimination may occur
through proxy variables.

Such evaluation supports responsible AI development and compliance with
fair processing principles under GDPR.

## 5. Data Minimization (GDPR Art. 5(1)(c))

Only variables necessary for the analysis of loan approval outcomes were retained
in the curated dataset.

The data engineering pipeline transforms raw application data into a structured
dataset suitable for analysis while removing unnecessary fields.

This process helps ensure that only relevant information is used in the modeling
and fairness evaluation process.

This process also supports privacy protection by ensuring that the
dataset used for analysis does not include unnecessary personal
information. Removing direct identifiers and limiting the dataset
to relevant attributes reduces the risk of re-identification and
aligns with the GDPR principle of data minimization (Article 5(1)(c)).

## 6. Data Governance and Security

Project data is organized into structured storage layers:

- [data/raw](../data/raw) – original dataset – original dataset
- [data/curated](../data/curated) – processed dataset used for analysis
- [data/artifacts](../data/artifacts) – data quality outputs and summaries

This layered data architecture supports transparency, reproducibility,
and responsible data management.

## 7. Summary of GDPR Compliance

Based on the analyses conducted, the project demonstrates several practices that
align with GDPR principles:

- Data quality checks ensure accuracy of the dataset
- Bias analysis helps detect potential discriminatory outcomes
- Data processing is limited to the defined project objective
- Structured data storage improves governance and transparency

While the dataset is used for academic analysis rather than real-world deployment,
the governance framework implemented in this project reflects best practices
for responsible data processing.
