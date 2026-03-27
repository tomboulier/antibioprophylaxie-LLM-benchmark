# Scoring Methodologies for Medical LLM Benchmarks

Research report -- March 2026

## 1. Landscape of Medical Benchmark Scoring

### 1.1 AMEGA (Autonomous Medical Evaluation for Guideline Adherence)

Published Dec 2024 in NPJ Digital Medicine. The closest benchmark to our use case: it evaluates LLM adherence to **medical guidelines** specifically.

- **Structure**: 24 clinical cases, 163 questions, 1497 weighted evaluation criteria across 13 specialties.
- **Scoring**: Multi-layered hierarchical scoring (criterion > section > question > case). Each criterion has a numeric weight defined by expert physicians.
- **Grading method**: GPT-4 as autonomous evaluator, calibrated against physician ground truth.
- **Key insight**: Criteria are pre-defined and weighted, making the rubric deterministic even though an LLM applies it. The rubric itself is the source of reproducibility.
- Source: [Nature, NPJ Digital Medicine](https://www.nature.com/articles/s41746-024-01356-6) | [GitHub](https://github.com/DATEXIS/AMEGA-benchmark/)

### 1.2 HealthBench (OpenAI)

Published May 2025. The largest physician-authored medical rubric benchmark.

- **Structure**: 5000 conversations, 48,562 unique rubric criteria authored by 262 physicians from 60 countries.
- **Scoring**: Each criterion has a point value from -10 to +10. Positive = reward correct behavior, negative = penalize harmful content. Total score = sum of met criteria / max possible.
- **Grading method**: GPT-4.1-based grader applies the rubric. Validated against physician agreement.
- **Variants**: HealthBench Consensus (34 high-importance dimensions), HealthBench Hard.
- **Key insight**: Boolean per-criterion evaluation (met/not met), then weighted aggregation. This is essentially a deterministic rubric applied by a probabilistic grader.
- Source: [OpenAI](https://openai.com/index/healthbench/) | [Paper PDF](https://cdn.openai.com/pdf/bd7a39d5-9e9f-47b3-903c-8b847ca650c7/healthbench_paper.pdf)

### 1.3 CSEDB (Clinical Safety and Effectiveness Database)

Published 2025 in NPJ Digital Medicine. Focus on safety and effectiveness dimensions.

- **Structure**: 2069 open-ended Q&A items across 26 clinical departments, 30 consensus-derived metrics.
- **Scoring**: Weighted and normalized across safety (critical illness detection, medication safety) and effectiveness (guideline adherence, diagnostic pathways). Average total score: 57.2%.
- **Grading method**: Automated assessment + manual concordance validation by 32 specialist physicians.
- **Key insight**: Explicit separation of safety vs. effectiveness scoring dimensions, with weighted consequence measures.
- Source: [Nature, NPJ Digital Medicine](https://www.nature.com/articles/s41746-025-02277-8)

### 1.4 LLMEval-Med

Published 2025. Real-world clinical benchmark with physician validation.

- **Structure**: 2996 questions from real EHR data across 5 medical domains.
- **Scoring**: 0-5 scale per dimension (instruction adherence, accuracy, effectiveness, readability, safety). Automated scoring run 3 times with randomization for robustness.
- **Grading method**: GPT-4o as judge + expert-developed checklists. Random physician sampling validates machine scores.
- **Key insight**: Triple-run randomized evaluation to reduce grader variance. Usability Rate metric (score >= 4/5).
- Source: [arXiv](https://arxiv.org/abs/2506.04078)

### 1.5 Health-SCORE

Published Jan 2026. Scalable rubric framework built on top of HealthBench.

- **Approach**: Generalizable rubric-based training and evaluation that reduces rubric development costs.
- **Key innovation**: Adaptive Precise Boolean rubrics -- granular yes/no targets instead of Likert scales, yielding higher inter-rater agreement and ~50% less evaluation time.
- **Key insight**: Boolean criteria are more reproducible than ordinal scales.
- Source: [arXiv](https://arxiv.org/abs/2601.18706)

## 2. Deterministic Scoring Approaches for Free-Text Medical Answers

### 2.1 Traditional NLP Metrics (Limited Applicability)

| Metric | Approach | Medical suitability |
|--------|----------|-------------------|
| Exact match | String equality | Only for MCQ or single-word answers |
| ROUGE | N-gram overlap | Poor correlation with medical quality; negative correlations reported in clinical tasks |
| BLEU | N-gram precision | Fails on paraphrases and medical synonyms |
| BERTScore | Contextual embedding similarity | Better semantic capture, but mixed results in clinical contexts (Pearson r = 0.28-0.44) |
| METEOR | Stems + synonyms | Slightly better than BLEU, but not medical-domain-aware |

**Conclusion**: Traditional metrics are inadequate for evaluating medical free-text answers. They do not distinguish "cefazoline 2g" from "cefazoline 1g" (both would score high on overlap).

### 2.2 Structured Entity Extraction + Rule-Based Scoring

The most promising **deterministic** approach for our use case:

1. **Extract structured fields** from the LLM answer (molecule, dose, duration, route, timing).
2. **Compare field by field** against ground truth using exact match or controlled synonyms.
3. **Score each field independently** with configurable weights.

This approach is used in clinical NER evaluation (F1 per entity type) and drug attribute extraction systems. For our antibioprophylaxie benchmark, this maps directly:

```
Expected: "cefazoline 2g IV, 30 min avant incision"
Extract:  molecule="cefazoline", dose="2g", route="IV", timing="30 min avant incision"

Scoring:  molecule_correct (1/0) * weight_molecule
        + dose_correct (1/0) * weight_dose
        + route_correct (1/0) * weight_route
        + timing_correct (1/0) * weight_timing
```

**Advantages**: Fully deterministic, reproducible, interpretable, no LLM grader needed.
**Limitations**: Requires structured ground truth and a parsing step (regex or small LLM).

### 2.3 MedScore: Decompose-then-Verify Pipeline

Published May 2025. Domain-adapted factuality evaluation for free-form medical answers.

- **Step 1**: Decompose answer into atomic medical claims (condition-aware).
- **Step 2**: Verify each claim against reference corpus (MedCorp) or original expert answer.
- Extracts 3x more valid facts than FActScore or VeriScore.
- Open source: [GitHub](https://github.com/Heyuan9/MedScore)

**Relevance**: Could be adapted for verifying that an LLM's free-text answer contains all required factual elements from the guideline.

## 3. Handling "Correct Answer, Different Formulation"

The benchmarks surveyed use several strategies:

### 3.1 Rubric Criteria (HealthBench, AMEGA)
Instead of comparing to a single reference string, define **what the answer must contain** as a checklist of boolean criteria. The formulation does not matter; only the presence of required information.

### 3.2 Synonym/Alias Tables
For drug names, maintain a controlled vocabulary:
```python
ALIASES = {
    "cefazoline": ["cefazoline", "cefazolin", "kefzol", "ancef"],
    "amoxicilline": ["amoxicilline", "amoxicillin", "clamoxyl"],
}
```
Deterministic and extensible. Used implicitly in clinical NER systems.

### 3.3 Claim Decomposition (MedScore)
Decompose both reference and candidate into atomic claims, then verify coverage. Handles reformulation naturally because verification is semantic, not lexical.

### 3.4 Structured Output Forcing
Force the LLM to respond in structured format (JSON), then compare fields. Eliminates the parsing problem entirely. Trade-off: constrains the LLM and may reduce naturalness.

## 4. Multi-Criteria Scoring (Molecule + Dose + Duration)

### 4.1 Weighted Checklist Pattern (Recommended)

Used by AMEGA and HealthBench. Each question has multiple independently scored criteria with weights:

```json
{
  "question_id": "Q1",
  "criteria": [
    {"id": "molecule", "description": "Mentions cefazoline", "weight": 3},
    {"id": "dose", "description": "Specifies 2g", "weight": 2},
    {"id": "route", "description": "IV administration", "weight": 1},
    {"id": "timing", "description": "30 min before incision", "weight": 2},
    {"id": "contraindication", "description": "Mentions allergy alternative", "weight": -2}
  ]
}
```

Score = sum(met_criteria * weight) / sum(positive_weights)

### 4.2 Hierarchical Scoring (AMEGA)

Criteria are grouped into sections (e.g., "Antibiotic choice", "Dosing", "Administration"), sections into questions, questions into cases. Scores aggregate bottom-up.

### 4.3 Safety-Weighted Scoring (CSEDB)

Critical safety criteria (e.g., wrong drug for allergic patient) carry higher negative weights than effectiveness criteria (e.g., suboptimal timing). This is essential for medical contexts.

## 5. Hybrid Frameworks: Deterministic + Semantic

### 5.1 RULERS (Jan 2026)

The most mature hybrid framework found:

- **Compile phase**: Transforms natural-language rubric into executable, versioned, immutable specification (position-independent checklist).
- **Execute phase**: Extraction agent retrieves evidence from text, scoring agent applies rubric to evidence only.
- **Calibrate phase**: Lightweight Wasserstein-based post-hoc calibration, no model fine-tuning.
- **Result**: Minimal variance on rubric reordering, high reproducibility.
- Source: [arXiv](https://arxiv.org/abs/2601.08654)

### 5.2 AutoSCORE (Sep 2025)

Two-agent pipeline:
1. **Extraction Agent**: Identifies structured components matching rubric criteria.
2. **Scoring Agent**: Assigns scores based only on extracted evidence.
3. Optional: Verification Agent for denoising, Feedback Agent for interpretability.

Particularly effective on complex, multi-dimensional rubrics.
- Source: [arXiv](https://arxiv.org/abs/2509.21910)

### 5.3 Proposed Hybrid for Our Project

Combine deterministic and semantic layers:

```
Layer 1 (Deterministic): Structured field extraction + exact matching
  - Regex/pattern-based extraction of molecule, dose, route, timing
  - Synonym table lookup
  - Score: 0 or 1 per criterion

Layer 2 (Semantic, optional): LLM-based rubric verification
  - For criteria that resist deterministic parsing (e.g., "mentions contraindication context")
  - Boolean rubric criteria applied by LLM grader
  - Score: 0 or 1 per criterion

Final score = weighted sum across all criteria
```

## 6. Actionable Recommendations for Our Benchmark

### Priority 1: Extend the Dataset Format

Add multi-criteria ground truth to `benchmark.md` / `benchmark.json`:

```json
{
  "expected_answer": "Cefazoline 2g IV",
  "scoring_criteria": [
    {"field": "molecule", "expected": ["cefazoline"], "aliases": ["cefazolin", "kefzol"], "weight": 3},
    {"field": "dose", "expected": ["2g", "2 g"], "weight": 2},
    {"field": "route", "expected": ["IV", "intraveineuse"], "weight": 1}
  ]
}
```

### Priority 2: Implement Structured Field Scoring

Replace `OpenScorer`'s simple substring matching with a multi-criteria scorer:

- Parse expected criteria from the question metadata.
- For each criterion, check if any expected value (including aliases) appears in the normalized answer.
- Return per-criterion results + weighted aggregate score.
- This remains **fully deterministic** and **stdlib-only**.

### Priority 3: Add Negative/Safety Criteria

Following CSEDB's approach, add criteria that penalize dangerous answers:

```json
{"field": "safety", "description": "Does NOT recommend antibiotic if contraindicated", "weight": -5}
```

### Priority 4 (Later): Optional LLM-Based Rubric Layer

For questions where deterministic matching is insufficient, add an optional LLM grader layer using the RULERS/AutoSCORE extract-then-score pattern. This should be:
- Opt-in per question (most questions should score deterministically).
- Run with temperature=0 and triple evaluation for robustness.
- Logged separately from deterministic scores for transparency.

### What NOT to Do

- Do not use ROUGE/BLEU/BERTScore for medical answer evaluation. They correlate poorly with clinical correctness.
- Do not rely solely on LLM-as-judge without a structured rubric. Reproducibility will be poor.
- Do not use Likert scales (1-5) for criteria. Boolean (met/not met) yields higher inter-rater agreement (Health-SCORE finding).

## Sources

- [AMEGA -- NPJ Digital Medicine, Dec 2024](https://www.nature.com/articles/s41746-024-01356-6)
- [AMEGA GitHub](https://github.com/DATEXIS/AMEGA-benchmark/)
- [HealthBench -- OpenAI, May 2025](https://openai.com/index/healthbench/)
- [HealthBench Paper](https://cdn.openai.com/pdf/bd7a39d5-9e9f-47b3-903c-8b847ca650c7/healthbench_paper.pdf)
- [CSEDB -- NPJ Digital Medicine, 2025](https://www.nature.com/articles/s41746-025-02277-8)
- [LLMEval-Med -- arXiv, Jun 2025](https://arxiv.org/abs/2506.04078)
- [Health-SCORE -- arXiv, Jan 2026](https://arxiv.org/abs/2601.18706)
- [MedScore -- arXiv, May 2025](https://arxiv.org/abs/2505.18452) | [GitHub](https://github.com/Heyuan9/MedScore)
- [RULERS -- arXiv, Jan 2026](https://arxiv.org/abs/2601.08654)
- [AutoSCORE -- arXiv, Sep 2025](https://arxiv.org/abs/2509.21910)
- [LLM-Rubric -- ACL 2024](https://aclanthology.org/2024.acl-long.745.pdf)
- [Medical NER Systematic Review](https://www.sciencedirect.com/science/article/pii/S1386505623001405)
