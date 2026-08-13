# Reproduction instructions

Create a Python 3.12 environment from `environment/requirements.lock`. Run `python scripts/verify_release.py` to verify every released byte, record count, publication table and privacy boundary. Full scientific reruns require the governed source files named and hashed in `manifests/ANALYTICAL_INPUT_MANIFEST.csv`; complete registry JSON is not included in this data-minimized release. Journal-facing figures use the frozen CSVs in `publication/` and the presentation rules in `docs/PUBLICATION_FIGURE_RENDERING.md`.
