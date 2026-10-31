# Pseudocode: Personal-Data Discovery & Privacy Evidence Engine (PS-019)

This document outlines the core algorithmic workflows, mathematical scoring formulations, and cryptographic verification routines powering the **AEGIS** scanning engine.

---

## 1. Overall Scanning Architecture

```text
ALGORITHM ScanInventory(TargetSources, RuleConfig, MetadataRegistry)
INPUT:
    TargetSources: List of CSV file paths and SQLite database file paths
    RuleConfig: YAML configuration containing weights (w_col, w_val, w_alg) and thresholds
    MetadataRegistry: Declared purposes and retention schedules loaded from metadata.csv
OUTPUT:
    EvidenceInventory: Table of profiled candidate personal data fields with confidence scores

BEGIN
    EvidenceInventory ← EmptyList()
    Detectors ← [NameDetector, EmailDetector, PhoneDetector, GovtIdDetector, DobDetector]

    FOR EACH Source IN TargetSources DO:
        IF Source is CSV THEN:
            ColumnMap ← ReadSampledCSV(Source, SampleLimit = 1000)
            DatasetName ← GetBaseName(Source)
            TableName ← GetFileStem(Source)
            FOR EACH (ColumnName, Values) IN ColumnMap DO:
                Record ← ScanColumn(ColumnName, Values, DatasetName, TableName, Detectors, RuleConfig, MetadataRegistry)
                Append Record TO EvidenceInventory
            END FOR
        ELSE IF Source is SQLiteDB THEN:
            TableMap ← InspectTablesAndSample(Source, SampleLimit = 1000)
            DatasetName ← GetBaseName(Source)
            FOR EACH (TableName, ColumnMap) IN TableMap DO:
                FOR EACH (ColumnName, Values) IN ColumnMap DO:
                    Record ← ScanColumn(ColumnName, Values, DatasetName, TableName, Detectors, RuleConfig, MetadataRegistry)
                    Append Record TO EvidenceInventory
                END FOR
            END FOR
        END IF
    END FOR

    RETURN EvidenceInventory
END
```

---

## 2. Multi-Signal Technical Confidence Scoring

```text
ALGORITHM ScanColumn(ColumnName, Values, DatasetName, TableName, Detectors, RuleConfig, MetadataRegistry)
INPUT:
    ColumnName: String header of the database or CSV column
    Values: Array of sampled string values
    Detectors: List of 5 data-class detectors
OUTPUT:
    DiscoveredFieldRecord: Technical evidence record with confidence and RoPA status

BEGIN
    TotalRows ← Length(Values)
    NonNullValues ← FilterNonEmpty(Values)
    NonNullRows ← Length(NonNullValues)
    NullRatio ← 1.0 - (NonNullRows / TotalRows) IF TotalRows > 0 ELSE 1.0

    BestEvidence ← NULL
    BestScore ← -1.0

    FOR EACH Detector IN Detectors DO:
        // Signal 1: Column Header Name Match
        (ColScore, ColRuleMatched) ← Detector.EvaluateColumnName(ColumnName, RuleConfig)

        // Signal 2 & 3: Value Pattern Match & Algorithmic Validation
        (ValPatternScore, AlgValidScore, MaskedSamples, MatchCount, ValidCount, PatternRule, ValidatorDesc) ← 
            Detector.EvaluateValues(NonNullValues, RuleConfig)

        // Null Sparsity Penalty Factor
        DensityFactor ← 1.0
        IF NullRatio > 0.8 THEN
            DensityFactor ← 0.60
        ELSE IF NullRatio > 0.5 THEN
            DensityFactor ← 0.85
        END IF

        // Exclusion Penalty if Column matched negative blacklist pattern
        IF ColRuleMatched STARTS WITH "Exclusion match" THEN
            DensityFactor ← DensityFactor * 0.20
        END IF

        // Compute Weighted Confidence Score
        W_Col ← RuleConfig.weights["column_name"]            // Default: 0.35
        W_Val ← RuleConfig.weights["value_pattern"]          // Default: 0.40
        W_Alg ← RuleConfig.weights["algorithmic_validation"] // Default: 0.25

        IF NonNullRows == 0 THEN
            OverallScore ← Round(ColScore * W_Col, 4)
        ELSE
            RawScore ← (ColScore * W_Col) + (ValPatternScore * W_Val) + (AlgValidScore * W_Alg)
            OverallScore ← Round(RawScore * DensityFactor, 4)
        END IF

        IF OverallScore > BestScore THEN
            BestScore ← OverallScore
            BestEvidence ← BuildEvidenceTrail(
                ColumnName, Detector.DataClass, OverallScore, ColScore,
                ValPatternScore, AlgValidScore, MaskedSamples, TotalRows,
                NonNullRows, NullRatio, MatchCount, ValidCount, ColRuleMatched,
                PatternRule, ValidatorDesc
            )
        END IF
    END FOR

    // Assign Confidence Tier
    IF BestScore >= RuleConfig.thresholds["high"] (0.75) THEN
        Tier ← "High"
        IsCandidatePII ← TRUE
    ELSE IF BestScore >= RuleConfig.thresholds["medium"] (0.45) THEN
        Tier ← "Medium"
        IsCandidatePII ← TRUE
    ELSE IF BestScore >= RuleConfig.thresholds["low"] (0.25) THEN
        Tier ← "Low"
        IsCandidatePII ← TRUE
    ELSE
        Tier ← "None"
        IsCandidatePII ← FALSE
    END IF

    // Link with RoPA Metadata Registry & Categorize Compliance Gap
    MetaLink ← MetadataRegistry.Lookup(TableName, ColumnName)
    GapStatus ← DetermineComplianceGap(IsCandidatePII, Tier, MetaLink.DeclaredPurpose, MetaLink.RetentionPeriod)

    RETURN BuildFinalRecord(BestEvidence, IsCandidatePII, Tier, MetaLink, GapStatus)
END
```

---

## 3. Verhoeff D5 Checksum Verification (Aadhaar UIDAI)

```text
ALGORITHM ValidateVerhoeff(NumberString)
INPUT:
    NumberString: 12-digit numeric string (e.g. Indian Aadhaar)
OUTPUT:
    Boolean: TRUE if Verhoeff check digit is cryptographically valid, FALSE otherwise

CONSTANTS:
    // Multiplication Table d (Dihedral group D5 multiplication)
    D_TABLE: 10x10 matrix of permutation group products
    // Permutation Table p
    P_TABLE: 8x10 matrix of index permutations
    // Inversion Table inv
    INV_TABLE: [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

BEGIN
    CleanDigits ← ExtractDigitsOnly(NumberString)
    IF Length(CleanDigits) != 12 OR CleanDigits[0] IN ('0', '1') THEN
        RETURN FALSE
    END IF

    ChecksumAccumulator ← 0
    ReversedDigits ← ReverseString(CleanDigits)

    // Traverse digits from right to left where index 0 is the check digit
    FOR Index FROM 0 TO Length(ReversedDigits) - 1 DO:
        Digit ← Integer(ReversedDigits[Index])
        PermutedValue ← P_TABLE[Index MOD 8][Digit]
        ChecksumAccumulator ← D_TABLE[ChecksumAccumulator][PermutedValue]
    END FOR

    RETURN (ChecksumAccumulator == 0)
END
```

---

## 4. Compliance Gap Determination

```text
ALGORITHM DetermineComplianceGap(IsCandidatePII, ConfidenceTier, DeclaredPurpose, RetentionPeriod)
INPUT:
    IsCandidatePII: Boolean
    ConfidenceTier: "High" | "Medium" | "Low" | "None"
    DeclaredPurpose: String or NULL
    RetentionPeriod: String or NULL
OUTPUT:
    (GapSeverity, RemediationGuidance)

BEGIN
    IF NOT IsCandidatePII THEN
        RETURN ("N/A (Non-PII)", "No compliance action required.")
    END IF

    IsPurposeMissing ← (DeclaredPurpose is NULL OR DeclaredPurpose == "")
    IsRetentionMissing ← (RetentionPeriod is NULL OR RetentionPeriod == "")

    IF IsPurposeMissing AND IsRetentionMissing THEN
        IF ConfidenceTier IN ("High", "Medium") THEN
            RETURN ("Critical Gap", "Urgent: Unregistered Personal Data. Add to RoPA, declare lawful processing purpose, and establish binding retention schedule.")
        ELSE
            RETURN ("High Gap", "Verify whether field contains true personal data; document declared purpose and retention limits.")
        END IF
    ELSE IF IsPurposeMissing THEN
        RETURN ("High Gap", "Missing declared lawful processing purpose. Define operational requirement under privacy policy.")
    ELSE IF IsRetentionMissing THEN
        RETURN ("Medium Gap", "Purpose declared, but retention schedule missing. Establish maximum storage limitation and automated purging window.")
    ELSE
        RETURN ("Declared", "Processing purpose and retention schedule are documented in compliance registry.")
    END IF
END
```
