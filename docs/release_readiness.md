# Final publication review

**Recommendation: GO for publishing this standalone portfolio repository.** The reviewed tree is independently implemented, its included materials passed the release checks, attribution and result claims are appropriately qualified, and the MIT license is scoped to the new standalone work. The historical test-protocol discrepancy remains disclosed as a methodological limitation; it is not treated as a publication blocker.

## Release checks

| Area | Finding |
| --- | --- |
| Independent implementation | The package, CLI, tests, prompts, synthetic fixtures/assets, and diagrams were written for this standalone repository. A comparison against tracked code and text in the private team repository found no substantial copied or adapted passage. The methods and research direction are explicitly credited as team-derived. |
| Public file safety | Release scanner passed. Included dataset-like materials are 20 invented CSV rows and static synthetic mock responses; images are abstract generated icons. No source video, dataset rows or identifiers, OCR/ASR, keyframes, real few-shot examples/prompts, cached responses, predictions, credentials, restricted files, report, or original Git objects are included. |
| Research/result attribution | All four report authors are credited. The README distinguishes the historical team experiment from the new software implementation and preserves Mahdi's stated role: full responsibility for System 1 and its audits; collaborative System 2 development; and proposal, development, and experimentation of the selected Prompt C dynamic five-shot strategy. |
| Metrics and charts | Test metrics and validation ablations were checked against committed aggregate artifacts. The README and charts identify the 74-example test split and 29-example validation set, report the +8.33-point fake-recall result alongside the precision/false-positive trade-off, and state the small-sample limits. |
| Test protocol | System 1's committed runner evaluates test metrics for eight variants, while the report describes a locked split. Whether the repeated evaluations influenced selection is unknown. The docs say this directly and avoid claiming a pristine one-time test. System 2's one recorded test artifact is described with the limits of that evidence. |
| License | Added MIT for the independently authored standalone software, synthetic material, and new documentation. The license expressly excludes the dataset, third-party works, and original DAT560 repository/report. `pyproject.toml` declares the SPDX `MIT` expression and distributes the license file. |
| Setup and demonstrations | Python 3.11 setup, tests, baseline/MLLM synthetic demos, and documentation/release audits are documented. The MLLM demo uses static fixtures and makes no network call. Runtime dependencies are declared and pinned; none are vendored. |
| CI and Git | GitHub Actions runs tests, demos, and both audits on push and pull request with read-only contents permission. Local Git is on `main`, has no commits or remote, and `.gitignore` excludes credentials, environments, caches, build output, runs, and restricted data paths. `.gitattributes` normalizes text and preserves image binaries. |

## Recorded research comparison

The original committed result artifacts support this descriptive comparison on 74 test examples (24 fake, 50 real):

| Configuration | Accuracy | Macro-F1 | Fake precision / recall | Real precision / recall | Fake true positives |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline A | 70.27% | 0.6793 | 53.33% / 66.67% | 81.82% / 72.00% | 16 / 24 |
| Baseline B | 75.68% | 0.7282 | 61.54% / 66.67% | 83.33% / 80.00% | 16 / 24 |
| Final MLLM | 71.62% | 0.7004 | 54.55% / 75.00% | 85.37% / 70.00% | 18 / 24 |

The final MLLM identified two additional fake videos, a +8.33 percentage-point recall increase over either baseline. Relative to Baseline B, fake precision is 6.99 points lower and the MLLM generated five additional false positives; its macro-F1 is also lower. Twenty-four fake cases are too few to establish a generalizable improvement. The historical result comes from the original team artifacts; the new standalone package does not rerun it.

## Verification evidence

The Windows CPython 3.11.9 verification run recorded:

- `python -m pytest -vv` — 16 passed.
- `python -m fakett_research.demo` — passed using synthetic data and static fixtures.
- The README's `fakett_research.mllm` mock-fixture command — passed without network access.
- `scripts/audit_release.py` — passed.
- `scripts/check_docs.py` — passed; checked JSON, SVG, and local Markdown links.
- `python -m pip wheel --no-deps . --wheel-dir dist` — passed with setuptools 77.0.3. The wheel declares `License-Expression: MIT` and bundles `LICENSE`.

GitHub-hosted Actions has not run because this local repository has no remote and the user explicitly asked not to publish yet. The workflow is configured and the same steps were exercised locally. The first hosted run will occur after the user publishes the repository.

## Publication boundary

This portfolio repository is separate from the original DAT560 repository, which remains private and unchanged. The local portfolio repository has no commits or remote. No commit, push, visibility change, or publication has been made in this review.

FakeTT dataset access remains subject to the dataset project's own terms. Do not add dataset material, examples, identifiers, source videos, or other restricted content to this repository. The repository's MIT license does not change those terms.
