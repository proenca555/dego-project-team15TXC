# DEGO Project - Team 15TXC

# # Team Members
- Bárbara Dias
- João Casanova
- Tiago Proença
- Getrude Mwatela

## Project Description
Bias and governance analysis of automated credit approval systems, developed for the DEGO course.  
The project evaluates potential algorithmic bias in credit scoring decisions and proposes governance mechanisms aligned with GDPR and the EU AI Act.

## Repository Structure
- README.md – project overview and findings summary
- data/
  - raw/ – original dataset
  - curated/ – cleaned dataset used for analysis
  - artifacts/ – intermediate data outputs
- notebooks/
  - 01-data-quality.ipynb – data quality assessment
  - 02-bias-analysis.ipynb – fairness and bias analysis
- src/ – reusable data engineering code
- reports/ – governance analysis report
- presentation/ – final presentation slides and recorded video

## Progress Tracking

### 03-03-2026
- Repository created
- Team members added
- Initial project structure defined

### 04-03-2026
- Data engineering pipeline completed (flatten JSON → curated dataset; standardize income/gender; parse dates/derive age; expand spending features; remove duplicates)
- Data quality profiling completed + key issues identified (e.g., missing DOB/age; inconsistent encodings; a few validity outliers)

### 05-03-2026
- Bias analysis initiated using curated dataset
- Implementation of fairness analysis techniques (e.g., approval rate comparison, disparate impact exploration)
- Start of presentation slide structure and initial content draft

### 06-03-2026
- Data governance analysis completed, including regulatory and ethical assessment
- Evaluation of compliance with GDPR and EU AI Act requirements
- Identification of governance risks (algorithmic bias, proxy discrimination, transparency issues, excessive automation)
- Development of governance policy recommendations (bias monitoring, human oversight, data governance policies, transparency mechanisms)
- Continued development of presentation slides

### 07-03-2026
- Refined bias analysis and updated slides with quantitative findings
- Added fairness metrics, approval rates, and statistical test results
- Expanded slides on gender, age, geographic, and model-based bias
- Improved presentation storyline and slide coherence

### 08-03-2026
- Refined governance analysis and aligned results with fairness metrics
- Finalized presentation slides including governance risks and recommendations
- Reviewed presentation timing and structure
- Started recording the final presentation video