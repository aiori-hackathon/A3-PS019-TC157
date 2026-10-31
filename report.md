# Technical Research & Implementation Report: Autonomous Personal-Data Discovery & Privacy Evidence Inventory

**Track:** Cybersecurity (AIORI-3)  
**Problem Statement:** Hackathon PS-019: Personal-Data Discovery and Privacy Evidence Inventory  
**Date:** October 2026  
**System Designation:** AEGIS Privacy Discovery Engine (v1.0.0)  

---

## Executive Summary

Enterprise data ecosystems frequently accumulate personal information across legacy CSV extracts, transaction logs, and relational databases without continuous metadata synchronization. Under modern privacy regulations—such as India's **Digital Personal Data Protection Act (DPDP Act 2023)** and the European Union's **General Data Protection Regulation (GDPR)**—data fiduciaries must maintain an up-to-date **Record of Processing Activities (RoPA)**, identify statutory identifiers, enforce purpose limitation, and execute storage limitation (retention schedules).

This project presents **AEGIS**, an autonomous personal-data discovery and privacy evidence inventory system. AEGIS scans unstructured/messy CSV files and multi-table relational databases to detect candidate personal data across five regulated classes: **Name**, **Email**, **Phone**, **Government ID (Aadhaar/PAN)**, and **Date of Birth**. Rather than making opaque or ungrounded predictions, AEGIS implements a transparent **3-signal confidence engine** combining column-header heuristics, regular expression value profiling, and cryptographic/structural algorithmic validation (including the **Verhoeff D5 dihedral group checksum** for Indian Aadhaar and PAN entity coding).

Across five messy synthetic CSV datasets and a 4-table SQLite vault containing decoy columns, obfuscated headers, null values, and mixed formats, AEGIS achieves a **Macro F1-Score of 91.11%** (**97.5% Recall**, **86.0% Precision**) and a **Binary PII Accuracy of 89.71%**. Crucially, the system maintains strict statutory segregation between **technical evidence** and **legal interpretation**: all lawful basis assignments are reserved exclusively for human legal counsel and persisted in an audit database.

---

## 1. Problem Statement & Regulatory Context

### 1.1 The Challenge of "Dark PII" and Unregistered Processing
Organizations frequently ingest customer records, support logs, and HR exports without automated tracking. Over time, tables with ambiguous identifiers (e.g., `contact_token`, `bday`, `emergency_contact`) become "Dark PII": personal data processed without an explicit lawful basis, documented purpose, or configured retention schedule.

### 1.2 Statutory Mandates
1. **Purpose Limitation (DPDP Act 2023 Sec 4 / GDPR Art 5(1)(b)):** Personal data may only be collected and processed for explicit, declared lawful purposes.
2. **Storage Limitation & Right to Erasure (DPDP Act Sec 8 / GDPR Art 5(1)(e)):** Data fiduciaries must retain data only as long as necessary to satisfy the declared purpose.
3. **Statutory Identifier Safeguards (UIDAI Regulations & Aadhaar Act):** 12-digit Aadhaar numbers require specialized handling (masking, Verhoeff check-digit verification) to prevent identity fraud.
4. **Separation of Concerns:** Automated tools can provide *probabilistic technical evidence* that a column contains personal data. However, determining the *lawful basis* (e.g., explicit consent vs. legitimate use vs. contract performance) is a legal judgment that cannot be delegated to an unsupervised algorithm.

---

## 2. Technical Architecture & Methodology

AEGIS uses a modular architecture structured into distinct, decoupled subsystems:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION LAYER                            │
│    5 Messy Synthetic CSVs             Enterprise SQLite DB (4 Tables)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   3-SIGNAL TECHNICAL DISCOVERY ENGINE                  │
│                                                                        │
│   Signal 1: Column-Name Heuristics    (Weight: 0.35, Exclusion Filter) │
│   Signal 2: Value Pattern Profiling   (Weight: 0.40, Regex Matchers)   │
│   Signal 3: Algorithmic Verification  (Weight: 0.25, Verhoeff / Series)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       COMPLIANCE AUDIT & LINKAGE                       │
│    RoPA Metadata Linker                Privacy Gap Severity Engine     │
│   (metadata.csv Cross-Check)          (Critical / High / Medium Gaps)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     HUMAN-IN-THE-LOOP LEGAL WORKBENCH                  │
│    SQLite Reviewer Notes DB            Glassmorphism Cyber Dashboard   │
│   (Lawful Basis / DPO Sign-Off)       (Streamlit + Plotly Visuals)     │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Multi-Signal Technical Confidence Scoring Formulation

For any given candidate column $c$ containing sample values $V = \{v_1, v_2, \dots, v_n\}$:

1. **Column-Name Signal ($S_{col} \in [0.0, 1.0]$):**
   Evaluates regular expression matches against configured class identifier tokens. If the column header matches a configured exclusion/negative pattern (e.g., `product_name`, `order_date`, `created_at`, `transaction_id`), an exclusion penalty $\delta_{excl} = 0.20$ is triggered.

2. **Value Pattern Signal ($S_{val} \in [0.0, 1.0]$):**
   Measures the empirical ratio of non-null sample values matching the structural regex pattern of data class $k$:
   $$S_{val} = \frac{\sum_{i=1}^{m} \mathbb{I}(\text{RegexMatch}(v_i, \text{Pattern}_k))}{m}$$
   where $m$ is the count of non-empty, non-null values.

3. **Algorithmic Validation Signal ($S_{alg} \in [0.0, 1.0]$):**
   Measures the ratio of pattern matches that pass rigorous domain-specific validation:
   $$S_{alg} = \frac{\sum_{i=1}^{m} \mathbb{I}(\text{ValidAlgorithm}(v_i, \text{Class}_k))}{\max(1, \sum_{i=1}^{m} \mathbb{I}(\text{RegexMatch}(v_i, \text{Pattern}_k)))}$$

4. **Null Sparsity Factor ($\rho_{density} \in [0.60, 1.0]$):**
   Penalizes sparse columns where the null ratio exceeds 50% or 80%.

5. **Overall Confidence Formula ($C \in [0.0, 1.0]$):**
   $$C = \left( w_{col} S_{col} + w_{val} S_{val} + w_{alg} S_{alg} \right) \times \rho_{density} \times \delta_{excl}$$
   with baseline weights $w_{col} = 0.35$, $w_{val} = 0.40$, $w_{alg} = 0.25$ configured in `rules.yaml`.

Confidence is tiered into four unambiguous levels:
- **High ($\ge 0.75$):** Multi-signal convergence with valid algorithmic proof.
- **Medium ($0.45 \le C < 0.75$):** Probable personal data (e.g., valid pattern with misleading column name).
- **Low ($0.25 \le C < 0.45$):** Weak or sparse indicators requiring reviewer validation.
- **None ($< 0.25$):** Non-PII technical field.

---

## 3. Class-Specific Detection & Cryptographic Engines

### 3.1 Government ID: Indian Aadhaar via Verhoeff Dihedral D5 Checksum
Aadhaar numbers are 12 digits long, formatted as `XXXX-XXXX-XXXX` or `XXXX XXXX XXXX`, starting with digits `2` through `9`. To prevent fraudulent data entry and false positives from random 12-digit integers, AEGIS executes the **Verhoeff Checksum Algorithm**.

The Verhoeff algorithm operates on the dihedral group $D_5$ (symmetries of a regular pentagon) using multiplication table $d$, permutation table $p$, and inverse table $inv$:
$$c = \sum_{i=0}^{11} d(c, p(i \pmod 8, a_i)) = 0$$
where $a_i$ represents the $i$-th digit processed right-to-left. A random 12-digit number has only a $10\%$ probability of matching the check digit, eliminating false alarms on decoy numerical tracking strings.

### 3.2 Government ID: Indian Permanent Account Number (PAN)
Indian Tax PAN cards follow the 10-character structure `[A-Z]{5}[0-9]{4}[A-Z]`. AEGIS validates:
- First three characters: Alphabetic series.
- Fourth character: Statutory entity code, where `P` = Individual (Person), `C` = Company, `H` = HUF, `F` = Firm, `T` = Trust, `A` = AOP, `B` = BOI, `L` = Local Authority, `J` = Artificial Juridical Person, `G` = Government.
- Fifth character: Surname initial.
- Next four characters: Sequential numeric digits.
- Tenth character: Alphabetic check character.

### 3.3 Contact Phone (Indian Telecommunications Allocation)
AEGIS parses Indian mobile numbers formatted with or without prefixes (`+91`, `0`, `91`, or raw 10-digit). The algorithmic validator verifies that the 10-digit national number starts with `6`, `7`, `8`, or `9`, conforming to the **Department of Telecommunications (DoT)** National Numbering Plan. Decoy 10-digit integers starting with `0`-`5` (e.g., shipping tracking numbers or epoch seconds) are rejected.

### 3.4 Email Addresses
Email detection combines RFC-5322 structural compliance parsing with domain syntax validation. Domain labels must have valid alphabetic Top-Level Domains (TLDs) of length $\ge 2$, rejecting malformed decoys such as `user@` or `user@domain`.

### 3.5 Date of Birth (DOB) vs. Event Timestamps
Distinguishing personal birthdates from event timestamps is a notorious privacy engineering challenge. AEGIS resolves this by combining:
1. Multi-format date parsing (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-Mon-YYYY`, etc.).
2. Negative keyword exclusion (`created_at`, `updated_at`, `timestamp`, `event_date`, `order_date`).
3. **Demographic Age Plausibility:** Valid birth years must fall between $1905$ and the current year ($2026$). Dates occurring in the future or within the last 6 months are rejected as non-DOB records.

---

## 4. Experimental Results & Benchmark Evaluation

### 4.1 Evaluation Dataset Description
AEGIS was benchmarked against a hand-labelled ground truth (`labels.csv`) across **68 distinct schema columns** derived from:
- `customers_messy.csv` (120 rows, misleading names like `contact_token`, nulls)
- `employees_hr.csv` (120 rows, corporate HR records, emergency contacts)
- `transactions_logs.csv` (120 rows, decoy tracking numbers, fulfillment dates)
- `kyc_onboarding.csv` (120 rows, valid Verhoeff Aadhaar, PAN cards)
- `support_tickets.csv` (120 rows, customer names, support engineer agents)
- `enterprise_vault.db` (4 SQLite tables: `user_profiles`, `billing_accounts`, `activity_telemetry`, `vendor_registry`)

### 4.2 Benchmark Metric Performance

| Data Class | Precision | Recall | F1-Score | Support | True Positives (TP) | False Positives (FP) | False Negatives (FN) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Email** | **1.0000** | **1.0000** | **1.0000** | 7 | 7 | 0 | 0 |
| **Phone** | **1.0000** | **1.0000** | **1.0000** | 8 | 8 | 0 | 0 |
| **Government ID** | **0.8000** | **1.0000** | **0.8889** | 8 | 8 | 2 | 0 |
| **Date of Birth** | **0.8000** | **1.0000** | **0.8889** | 4 | 4 | 1 | 0 |
| **Name** | **0.7000** | **0.8750** | **0.7778** | 8 | 7 | 3 | 1 |
| **Non-PII (Decoys)** | **0.9643** | **0.8182** | **0.8852** | 33 | 27 | 1 | 6 |

### 4.3 Headline Summary Metrics
- **Macro Precision (across 5 PII classes):** **86.00%**
- **Macro Recall (across 5 PII classes):** **97.50%**
- **Macro F1-Score:** **91.11%**
- **Binary PII Detection Accuracy:** **89.71%**
- **Binary PII F1-Score:** **90.67%**

---

## 5. Honest Error Analysis: Real False Alarms and Misses

Unlike artificial demonstrations claiming $100\%$ precision and recall on clean data, AEGIS deliberately incorporates realistic ambiguity. Below is an honest breakdown of the edge cases identified:

### 5.1 False Alarms (False Positives)
1. **Corporate Incorporation Date (`vendor_registry.incorporation_date`):**
   - *Observation:* Flagged as Date of Birth.
   - *Root Cause:* Values like `2018-05-18` represent valid calendar dates falling within the plausible human demographic range ($1905-2026$). Because the column header did not contain negative keywords like `created_at`, the parser scored it as a date.
   - *Remediation:* Add `incorporation_date` and `founding_date` to the corporate exclusion patterns in `rules.yaml`.

2. **Corporate Tax Identifier (`billing_accounts.tax_reg_no`):**
   - *Observation:* Flagged as Government ID (PAN).
   - *Root Cause:* In India, corporate entities (e.g., Companies, Partnerships) also receive 10-character PAN identifiers. The detector accurately recognized the PAN structural format, though from a strict privacy standpoint, an enterprise entity PAN is corporate data rather than personal data.

3. **Business Contact Names (`vendor_registry.contact_person`, `billing_accounts.billing_contact_name`):**
   - *Observation:* Flagged as Personal Name.
   - *Root Cause:* Both columns contain real human names (`Rajesh Kumar`, `Anita Desai`) of business representatives. While technically personal data under GDPR/DPDP, organizations often classify them as B2B business metadata.

### 5.2 Misses (False Negatives)
1. **Support Engineer Agent Name (`support_tickets.assigned_agent`):**
   - *Observation:* Classified with borderline confidence due to single-word nicknames or sparse initials in synthetic tickets.
   - *Remediation:* Adjust minimum name token count thresholds when column names contain `agent` or `operator`.

---

## 6. Privacy Compliance Gap Analysis

AEGIS cross-references all discovered candidate PII against `metadata.csv`. Across 40 discovered personal data fields:
- **Compliant (Declared Purpose & Retention):** 25 fields ($62.5\%$).
- **Critical Gaps (Missing Purpose AND Retention):** 8 fields ($20.0\%$).
  - Examples: `customers_messy.bday`, `employees_hr.emergency_contact`, `transactions_logs.buyer_email`, `enterprise_vault.user_profiles.birthdate`.
- **High / Medium Gaps (Missing Retention Schedule):** 7 fields ($17.5\%$).
  - Examples: `customers_messy.contact_token`, `customers_messy.aadhaar_num`.

Each gap is tagged with automated **Remediation Guidance** (e.g., *"Urgent: Unregistered Personal Data. Add to RoPA, declare lawful processing purpose, and establish binding retention schedule"*).

---

## 7. Limitations & Future Roadmap

### 7.1 Current Limitations
1. **Sampling vs. Exhaustive Scanning:** To ensure rapid performance on gigabyte-scale repositories, AEGIS inspects the first $1,000$ rows. If personal data appears only after row $50,000$, it will not be detected.
2. **Contextual Text Fields:** Free-text unstructured notes (e.g., customer complaints) containing embedded PII require Natural Language Processing (NLP/Named Entity Recognition) rather than columnar profiling.
3. **Multi-Jurisdiction Identifiers:** Current government ID validation focuses primarily on Indian statutory IDs (Aadhaar, PAN).

### 7.2 Future Roadmap
- **Phase 2:** Integrate lightweight on-device NER (SpaCy / Hugging Face Transformers) for unstructured text fields.
- **Phase 3:** Expand international statutory identifiers (US Social Security Numbers with Luhn check, UK National Insurance, Singapore NRIC).
- **Phase 4:** Automated differential privacy masking connectors for direct SQL database integration.

---

## 8. Statutory Disclaimer

> **TECHNICAL EVIDENCE ONLY • NOT LEGAL ADVICE**  
> The AEGIS system produces probabilistic technical evidence and statistical heuristics indicating the likelihood of personal data presence. It does not provide legal advice, nor does it make lawful basis determinations under the Digital Personal Data Protection Act (2023), GDPR, or any other privacy regulation. Lawful basis assessment, RoPA validation, and statutory compliance determinations must be performed by qualified legal counsel and designated Data Protection Officers.
