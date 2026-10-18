# Contributions and provenance

## Team authorship

The DAT560 project report names four authors: **Abel Segaye, Azhar Ahmad, Bashar Albittar, and Mahdi Nasser**. Preserve all four names in portfolio credits.

Mahdi's contribution description here is based on his direct clarification:

- **System 1:** full responsibility for the TF-IDF + Logistic Regression baseline and the connected research work: dataset investigations, preprocessing and OCR/ASR quality audits, leakage and duplicate checks, baseline experiments, evaluation, and analysis.
- **System 2:** collaborative implementation and improvement. Teammates developed the initial implementation with his assistance. Mahdi proposed and developed the selected Prompt C strategy with dynamic five-shot retrieval, separate text/visual analysis, and decision-level fusion; he also explored prompts, configurations, and evaluation approaches.

This description does not assign exclusive ownership of the whole System 2 architecture or team project to Mahdi.

## Git-history evidence

The history was reviewed locally in the private academic repository. The following commits corroborate activity and sequence; a commit author is not, by itself, proof of who conceived a research idea or owns every resulting work.

| Evidence | What the history records |
| --- | --- |
| 7c150d8 (2026-04-07), Mahdi | Added the System 1 modeling and audit sources, including TF-IDF/logistic-regression code, OCR/ASR quality analysis, duplicate/leakage checks, and evaluation. |
| bf91473, 1032b0a, faae079, Mahdi | Subsequent System 1 result/reproducibility/final-edit work. |
| a3f9c49 and 3c09c8f (2026-04-19), Segayeabel | Earlier System 2 prompting pipeline and path changes. |
| 0c5bd90 (2026-04-21), author identity “x” | A modification to the initial System 2 run/prompt files. The history does not map this identity to a report author. |
| 4fbaf19 (2026-04-22), Mahdi | Added the separate Prompt C text and visual prompt files and updated the pipeline. |
| 3fb60dd (2026-04-24), Mahdi | Added the dynamic few-shot pool builder and the Prompt C structural-ablation runner and related experiments. This historical commit also contains restricted sample-derived files; none are included here. |
| 563e004 (2026-04-24), Mahdi | Committed the recorded best-validation result artifact. |
| c097036 (2026-04-24), Mahdi | Committed the recorded final test result artifact. |

Git author metadata is not a complete accounting of each person's work, so the portfolio credits the four report authors and only gives a detailed role statement for Mahdi where the contribution history and his direct account support it. It does not infer individual roles for the other authors or publish private commit email addresses.

## Standalone project provenance

The Python package, CLI, tests, fixture data, images, SVGs, and README wording in this standalone directory were authored afresh for this portfolio release. No Python source, real prompt text, few-shot example, dataset row, keyframe, prediction, report page, or Git object was copied into it.

The implementation does re-create the project's broad methods and interfaces—TF-IDF + Logistic Regression, Prompt C's text/visual decomposition, dynamic example retrieval, structured model outputs, and decision fusion. These concepts, project framing, selected configuration, and historical results derive from the team's work and report. Treat this as an independent software reimplementation with team-derived research context, not as an unrelated project or a determination that those ideas and descriptions are individually owned.

The historical metrics are aggregate values transcribed and checked against the original result artifacts. The synthetic demo and its mock responses are newly invented and are not a reproduction or rerun of FakeTT.

## Public credit and license scope

The public README credits all four report authors and describes Mahdi's contribution using his account: full responsibility for System 1 and its audits; collaborative System 2 development; and proposal, development, and experimentation of the selected Prompt C dynamic five-shot strategy. It avoids assigning exclusive System 2 authorship or attributing roles to teammates beyond what the evidence supports.

The [MIT license](../LICENSE) applies to the independently authored standalone software, synthetic fixtures/assets, and new documentation in this repository. It does not grant rights to the FakeTT dataset, third-party materials, or the original DAT560 team repository/report. No such restricted material is included. Historical results remain attributed to the team's committed artifacts and report.
