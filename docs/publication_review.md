# Final GitHub publication review - 25 October 2026

Recommendation: publish only the reviewed current files in a new independent repository. Preserve the original repository and private research locally. The existing Git history remains unsuitable for public publication. No history rewrite, staging, commit, push or remote visibility change was performed.

## Verification

- Full local suite: 411 tests ran in 193.753 seconds; no failures or errors; Python process exit 0.
- Public-only allowlisted copy: 411 tests discovered in 40.927 seconds; 38 optional private-data/Git checks skipped; no failures or errors; process exit 0. No private data directory, credentials, original Git metadata or virtual environment was copied. This run used the existing installed dependencies.
- Public research tests: all three passed, including exact public/private statistical parity and a public-only Streamlit launch with credential variables removed and external socket/HTTP connections blocked. Default metrics remain 5,023 collected, 3,138 successfully classified, 1,778 relevant and 1,111 selected core-industry advertisements. Usable-evidence counts remain 1,035 overall and 611 core-industry.
- Windows errors are real and must not be omitted: Streamlit/Python temporary-directory finalizers print PermissionError / WinError 5 after successful test completion. The Python test processes exit 0 despite those finalizer errors.
- An initial deeply nested public-copy run failed with 24 errors and 38 skips: mock checkpoint filenames reached 273-274 characters and raised FileNotFoundError. Repeating the same allowlist and tests from a shorter path passed. README now recommends a short Windows checkout path. No research code or results were changed to bypass this issue.
- Fresh Windows installation: created a separate Python 3.14 virtual environment, installed the complete requirements from public PyPI using binary wheels (exit 0), and passed pip check and Streamlit/pandas/Plotly imports. The public-only copy then passed all 411 discovered tests with 38 expected skips in 23.679 seconds, process exit 0. Temporary-directory finalizer errors also appeared after that successful run. This verifies a fresh virtual environment on Windows, not a separate freshly provisioned computer.
- Existing environment: pip check reports no broken requirements. Public PyPI resolution with installed packages ignored succeeded for Windows CPython 3.14 using binary wheels. The initial default-index attempt failed because this execution environment sets PIP_NO_INDEX=1; it is not evidence that the dependency pins are unavailable.

## Current publication scope

Nothing is staged. Current tracked files and unignored candidates have no detected credential matches, saved notebook outputs, hardcoded home paths, syntax errors or files over 2 MB. Credential scanning uses heuristic patterns and exact local credential comparisons; it cannot prove every possible secret is absent. Binary screenshots are not certified by a text scanner.

The 11 untracked files under results photos/ are generated outputs and excluded from the publication allowlist. Do not use git add . in the original workspace. Private data, .env, secrets, caches, checkpoints, local archives, logs, virtual environments and temporary verification artifacts are excluded. .env.example and .streamlit/config.toml are intentionally public.

The updated docs/publication_files.txt lists exactly 130 approved file paths, including dashboard/presentation.py and tests/test_dashboard_redesign.py. Copy only these files into an empty independent directory. Never copy .git or use a clone, fork, mirror, or push --all to create the clean-history publication.

## Historical exposure remains

The current review scanned 191 blobs reachable through all local refs and found no credential-pattern or exact-local-credential matches. It reconfirmed:

- notebooks/01_explore_api.ipynb, blob 66d90b0bb573262ae9a39f5a345b35e618482639: seven saved outputs, two email-pattern occurrences, local paths and advertisement-derived fields. This blob is reachable from branch history.
- notebooks/02_explore_jobs.ipynb, blob cfc6ef454279442fccb20e8a058d4c3c40913df6: 15 saved outputs and local paths, with no email-pattern occurrences. It is reachable through local snapshot refs, outside the inspected branch/remote/tag histories.
- Eighteen private data-file blobs remain in local snapshot refs. A review CSV has 24 email-pattern occurrences; overlapping Data Engineer exports have 7, 2 and 5. These are occurrence counts, not unique contacts. No values were reproduced in this report.

Clearing current notebook outputs does not remove historical blobs. A normal branch push still carries its historical notebook. A mirror push or copying .git can also disclose local snapshot material. Retain the original repository privately and publish a new history from the allowlist. Remote-only refs, GitHub visibility, caches, forks, artifacts, prior clones and unreachable objects were not audited or changed. No claim is made that previously published material can be recalled.

The checker reports historical notebook findings but its exit status does not fail solely on historical notebook outputs; review its JSON findings as well as its exit code.

## Windows installation instructions

README now separates Windows PowerShell and macOS/Linux setup. Windows uses the explicit virtual-environment Python executable, avoiding Activate.ps1 and execution-policy changes. Python 3.14 x64 and Git must already be installed. Package installation requires package-index access; dashboard viewing requires no research API key. Prefer a short checkout path when running the complete tests.

## Publication decision

Use a new clean-history repository, not the existing history. Keep Windows cleanup errors and the long-path constraint documented; neither invalidates the verified public dashboard results. Review the staged allowlist in the new repository before manually committing and publishing. Research results, extraction evidence, caches and checkpoints were not modified.
