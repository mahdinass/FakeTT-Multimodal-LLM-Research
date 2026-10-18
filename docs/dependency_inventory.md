# Dependency inventory

Recorded from the installed distribution metadata in the Python 3.11.9 verification environment on 2026-10-18. Application dependencies are pinned in `pyproject.toml`. Transitive versions below describe this verification run; they are not cross-platform lock pins.

| Distribution | Version | Metadata license field |
| --- | ---: | --- |
| fakett-research | 0.1.0 | MIT (standalone software; see repository LICENSE scope) |
| requests | 2.32.3 | Apache-2.0 |
| scikit-learn | 1.6.1 | BSD 3-Clause License |
| pytest | 8.3.5 | MIT |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| scipy | 1.17.1 | License text present in metadata; see the installed distribution for full notices |
| joblib | 1.6.0 | BSD-3-Clause |
| threadpoolctl | 3.7.0 | BSD-3-Clause |
| urllib3 | 2.8.0 | MIT |
| certifi | 2026.10.18 | MPL-2.0 |
| charset-normalizer | 3.5.2 | MIT |
| idna | 3.20 | BSD-3-Clause |
| iniconfig | 2.3.1 | MIT |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.7.0 | MIT |
| colorama | 0.4.6 | No license field in installed Core Metadata |
| cloudpickle | 3.1.2 | BSD-3-Clause |

The isolated build environment uses `setuptools==77.0.3` and `wheel==0.45.1` as specified in `[build-system]`. Neither build tool is a runtime dependency. This inventory does not grant rights to the FakeTT dataset, third-party works, original team repository, or report. Confirm dependency license notices against the exact distributions if redistributing a built artifact.
