# Public research snapshot, 24 October 2026

Fresh clones load `examples/public_research`, without credentials, private data,
network access or classification. Local completed publications still take priority;
`JOBS_DASHBOARD_DATA` overrides discovery. The sidebar's Fictional demo selection
loads the six synthetic examples with a warning. Previously the only committed
dataset was that demo, because `/data/` is intentionally ignored by Git.

## Source and publication review

Arbetsförmedlingen's [official dataset catalogue](https://data.arbetsformedlingen.se/dataset/job-ads/)
lists JobSearch and Historical advertisements under Creative Commons CC0 (reviewed
24 October 2026). Source attribution is retained here and in the public manifest.
This is a derived statistical release, not a republication of the source database.
CC0 is not a privacy clearance: see its [limitations](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en)
and the European Commission's [personal-data explanation](https://commission.europa.eu/law/law-topic/data-protection/data-protection-explained_en).
Names and contact details in public advertisements can still be personal data.

The release contains 1,488 counted profiles representing 1,778 advertisements.
Profiles group identical analytical attributes and deduplicated normalized facts.
There are no original IDs, ID hashes, crosswalks, titles, employer names, publication
dates, URLs, descriptions, quotes, reasoning, offsets, model responses or source
metadata facts. Only category/scope/opportunity/multi-role/audit flags, geographic
labels, seniority, language statuses, usable-evidence flags and normalized
requirements with modalities and numeric experience bounds survive. Geographic
labels and normalized requirement vocabularies were inspected before export.
`tools/build_public_research.py` specifies the exact allowlist; no arbitrary fields
are copied from private manifests or records. Profile order depends only on their
public content, never source IDs or source ordering.

This minimizes identification risk; it is not a proof of irreversible anonymity.
Rare combinations of municipality, category and skills may allow matching to a
public job posting. These are characteristics of advertised roles, not employee
or applicant records; the release contains no person-level attributes or contact
fields. Small cells are retained to reproduce the requested exact charts and
joint filters. Do not join profiles to people or treat profiles as people. The
runtime creates internal `profile-unit-*` counting keys with no source mapping.

## Collection and methodology

The intended inclusive publication-date window is **21 April through 21 October
2026**, using Swedish calendar dates. Keyword searches of JobTech JobSearch
(active) and Historical (removed) APIs, geography checks and ID deduplication
produced 5,023 candidates. Search terms are in `config/search_terms.json`; API,
pagination, archive lag and date limitations are in [API notes](api_notes.md).
This is not a census; collection during the final day may miss later postings.

Saved GPT-4.1 Mini classifications assign relevance, primary category, scope and
opportunity flags. The Step 7 reconciler prefers accepted Step 3F 1.1 decisions,
otherwise valid historical decisions, with latest accepted within a version.
Exact-source validated cache reuse is allowed; no classification is performed
during export or dashboard use. Inclusion requires saved relevant status, valid
version-specific schema and supporting evidence matching the original source.
Irrelevant, uncertain, missing, invalid, failed and unknown outcomes are excluded.
The historical v3 audit is an optional quality filter, not a main inclusion gate.
See [Step 7 policy](step7_ai_relevant_policy_v1.md), versioned prompts and
`src/run_step7.py`. Source grounding does not establish classification correctness;
the findings are provisional and have not been independently human-verified.

Existing deterministic rules extract normalized skills, language, education,
experience and employment metadata. Original extracts retain source excerpts and
offsets privately. Required, preferred and required-alternative facts count as
requested qualifications; mere mentions and ambiguity are separately selectable.
Language statuses resolve conflicting evidence conservatively. Missing evidence
does not mean a requirement is absent. Scope precedence is opportunities, academic
research, adjacent/governance/core lanes; legacy scopes may be category-derived.
Multi-role status is separate. Secondary categories do not add advertisements.

## Exact denominators and parity

| Measure | Distinct advertisements |
|---|---:|
| Collected candidates (unfiltered) | 5,023 |
| Successfully classified, including source-validated reuse (unfiltered) | 3,138 |
| Accepted AI-relevant, all scopes | 1,778 |
| Default core-industry view | 1,111 |
| Usable requirement evidence, all scopes | 1,035 |
| Usable requirement evidence, default core | 611 |
| Recorded strict v3 audit approval, all scopes | 214 |

The 1,360 classified candidates outside the relevant release are not all necessarily
irrelevant; the release does not infer statuses for them. The remaining 1,885
collected candidates are not successfully classified. Collection/classification
totals never change with filters. Charts count distinct advertisements in the
current filters, including jobs without evidence; language tables additionally
report specified-status denominators. Overlapping skills, education alternatives,
modalities and metadata must not be summed as exclusive shares. Each primary
category/scope distribution counts an advertisement once. The 196 additional
IDs with identical title/description remain distinct; advertisements are not
unique vacancies, employers or market-demand estimates.

All statistical counts, filters and charts are retained. Deliberate reductions:
the source-ID coverage download and advertisement/evidence explorer are withheld;
the experience table groups numeric bounds/modality and counts distinct ads
instead of showing excerpts or individual records. Repeated equal facts are
deduplicated without changing any distinct-ad statistic. No suppression, sampling
or rounding is applied. Statistical reproduction is possible publicly; independent
rechecking of AI decisions or extractor evidence requires the private sources.

## Publish and keep private

The following new files are intended for GitHub publication:

- `examples/public_research/profiles.jsonl`
- `examples/public_research/public_manifest.json`
- `examples/public_research/step7_summary.json`
- `tools/build_public_research.py`
- `tests/test_public_research.py`
- `docs/public_research.md`

Updated `src/dashboard_data.py`, `dashboard/app.py`, `tests/test_portfolio.py`,
`README.md`, and the linked repository documentation are also public source.

Keep **all `data/` private**, including the finalized
`data/processed/step7-expanded-20261024/` (full JSONL/CSV advertisements, evidence,
coverage IDs, classifications, audit histories and private manifests), raw API
responses, intermediate datasets, `.llm_cache`, checkpoints and request ledgers.
Also keep `.env*` except empty `.env.example`, `.streamlit/secrets*.toml`, `.aws/`,
`.ssh/`, credential files, logs, `.local-archive/`, notebook outputs/checkpoints,
virtual environments and caches private. Do not publish an ID crosswalk. Existing
ignore rules remain active. No local research data or Git history is rewritten.

The history scan found pre-existing saved outputs and local paths in two reachable
notebook blobs: `notebooks/01_explore_api.ipynb`
(`66d90b0bb573262ae9a39f5a345b35e618482639`) and
`notebooks/02_explore_jobs.ipynb`
(`cfc6ef454279442fccb20e8a058d4c3c40913df6`). Their outputs contain advertisement/
employer fields; the first also has two email-pattern matches. These historical
blobs must be treated as private advertisement-derived material. Current notebook
files have cleared outputs. Publishing the new files does not remove older blobs
from an existing repository. The existing full history therefore cannot be
certified as sanitized. History was preserved as requested; any separate history
remediation or clean-history publication requires a distinct decision. The
heuristic scan detected no credential matches but cannot prove their absence.

The [final publication review](publication_review.md) distinguishes normal branch
history from private local snapshot refs and records additional research-data
blobs held by those snapshot refs. Use its clean-repository recommendation and
exact publication file list before publishing.

Rebuild offline with `python -m tools.build_public_research`; this requires the
private finalized source, but dashboard execution and public tests do not.

## Verification performed

On 24 October 2026, the local suite ran 409 tests with no failures. A separate
copy of tracked and unignored public files, without `.git`, `data/`, credentials
or dashboard overrides, ran the same 409 tests: no failures, 38 optional
private-data/Git checks skipped. Dependencies were reused from the installed
environment; installation on a second operating system was not performed.
The new Streamlit test also blocks external socket connections and HTTP requests,
checks 5,023 / 3,138 / 1,778 / 1,111 metrics, and exercises audit/demo selection.
Parity checks cover every chart's underlying data across all scope, category,
region, seniority, audit, opportunity and multi-role filter partitions, plus
joint filters. Deterministic projection equality verifies that the public profiles
retain the joint distribution used for arbitrary combinations. Existing Step 7
preservation-manifest hash checks passed. `pip check`, `git diff --check` and the
current-file repository security scan passed. The historical exceptions are
documented above. The Windows test environment also emitted temporary-directory
cleanup permission warnings after the local test result; these did not fail test
assertions, and the separate public-copy subprocess exited successfully.
