# Source, dataset, and rights audit

## Provenance: what is new and what is derived

This portfolio directory is separate from the private DAT560 repository. Its Python modules, tests, prompt wording, synthetic CSV rows, mock responses, abstract icons, SVGs, and README were written afresh for this standalone implementation. No original Python file, prompt file, sample row, keyframe, source video, per-sample output, report page, credential, or Git object was copied.

The reimplementation follows the group's described research design: TF-IDF + Logistic Regression; separate Prompt C text and visual branches; dynamic retrieval; structured predictions; and decision-level fusion. These methods and the selected final configuration are derived from the team's research and artifacts. The historical metric numbers in the portfolio are aggregate values transcribed from committed result JSONs. The narrative also summarizes the course report. This is clean-room software implementation, not independent ownership of the group's shared research design, project name, or findings.

| Material in this release | Provenance | Public-release status |
| --- | --- | --- |
| Python package, tests, CLI, release scanner | Newly written standalone code; algorithmic shape follows the team's reported methods | MIT applies to this independently authored implementation |
| Prompt templates | New wording without real FakeTT examples | Prompt C concept and selected strategy are team-derived; team credit is retained |
| Synthetic CSV, static responses, generated icons | Invented for software-path verification | Safe to include after the documented scan |
| Architecture and results charts | Newly drawn from verified historical summaries | Labeled as a summary of the team's approach and recorded results |
| Historical metrics and validation ablations | Read from original committed aggregate result artifacts; no row-level data reproduced | Attributed to the team; sample-size and protocol caveats remain visible |
| FakeTT dataset, split metadata, extracted OCR/ASR, frames, videos, few-shot examples | Original access-controlled research material | Excluded; obtain separately under the dataset project's access terms |
| Third-party libraries | Installed as dependencies, not copied into the source tree | Use each dependency under its own license; see dependency inventory |

## Excluded material and credentials

No original data splits or identifiers, sample metadata, OCR/ASR content, keyframes, videos, feature files, real-example prompts, dynamic/fixed few-shot banks, model responses, predictions, caches, pickles, audit CSVs, course PDF, source repository history, local API endpoint, or credential is included. The only data-like files are the 20 invented demonstration rows, two generated icons, and static synthetic fixture responses.

The standalone release scan checks token-like patterns, credential files, common restricted media/model extensions, local Windows paths, the former institutional endpoint, oversized files, and non-synthetic image locations. It passed after the portfolio edits. A normalized eight-token-shingle comparison against 28 tracked team Python files found a maximum Jaccard overlap of 3.97%; the new prompt text had a maximum overlap of 0.22% against 11 tracked team text files. The public software was written afresh; these low overlaps are consistent with common language and interfaces, not copied or substantially adapted code. This practical source comparison is not a legal opinion. The standalone Git repository has no commits or older objects that could contain excluded material.

## Original Git-history review

The source repository has no license. History supports the contribution account in [contributors.md](contributors.md): the System 1 baseline and audit source landed under Mahdi's author identity; initial System 2 code includes teammate-authored work; Mahdi's later commits include Prompt C branches, dynamic-pool builder, structural ablations, validation result, and final test result. The report names Abel Segaye, Azhar Ahmad, Bashar Albittar, and Mahdi Nasser. The public documentation credits every report author and does not infer unsupported individual roles or publish private email addresses.

The history also contains test-derived media and other source material. None of that historical tree or its objects was copied into this project. The standalone repository currently has an empty Git history and no remote.

## Rights boundary

The MIT license covers the independently authored software, synthetic material, and new documentation in this portfolio repository. It does not grant rights to the FakeTT dataset, third-party works, or the original DAT560 repository/report. No such restricted material is included. No specific confidentiality, contractual, intellectual-property, or institutional restriction on the included software, general methods, or attributed factual aggregate results was identified in this review.

The original [FakingRecipe project](https://github.com/ICTMCG/FakingRecipe) manages access to its research dataset. This portfolio release contains none of that dataset or its examples.

## Dependencies

Dependencies are declared rather than vendored. See [dependency_inventory.md](dependency_inventory.md) for the installed runtime/development inventory and build requirements. Keep required third-party notices with any redistributed software artifact.
