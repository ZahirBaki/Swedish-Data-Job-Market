"""Offline allowlist export of dashboard profiles; never writes to private data."""
import argparse
from collections import Counter
import json
from pathlib import Path

from src.dashboard_data import load_dataset

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'examples/public_research'
JOB_FIELDS = ('ai_primary_category', 'primary_category_label', 'reporting_scope',
              'analysis_scope', 'ai_scope', 'analysis_opportunity_types',
              'opportunity_group', 'multi_role_group', 'strict_audit_approved',
              'region', 'municipality', 'seniority', 'swedish_requirement',
              'english_requirement', 'requirements_data_usable')
FACT_FIELDS = ('kind', 'value', 'modality', 'stated_years', 'minimum_years',
               'maximum_years', 'bound_type')
KINDS = ('programming_language', 'cloud_platform', 'data_tool', 'education',
         'experience', 'language', 'employment_type', 'working_time', 'work_arrangement')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':'))


def build(source, destination=DESTINATION):
    source, destination = Path(source), Path(destination)
    if destination.resolve().is_relative_to((ROOT / 'data').resolve()):
        raise ValueError('Public output must not be inside private data')
    jobs, facts = load_dataset(source)
    totals = json.loads((source / 'step7_summary.json').read_text(encoding='utf-8'))
    if len(jobs) != 1778 or totals['expanded_total'] != 1778:
        raise ValueError('Expected finalized 1,778-ad Step 7 publication')
    grouped = {key: group for key, group in facts.groupby('advertisement_id')}
    profiles = Counter()
    for row in json.loads(jobs[list(('advertisement_id', *JOB_FIELDS))].to_json(orient='records')):
        identifier = row.pop('advertisement_id')
        group = grouped.get(identifier, facts.iloc[:0])
        # Deduplicate repeated excerpts: every dashboard statistic counts distinct ads.
        normalized = group[group.kind.isin(KINDS)][list(FACT_FIELDS)].drop_duplicates()
        records = json.loads(normalized.to_json(orient='records'))
        profiles[canonical(dict(attributes=row, facts=sorted(records, key=canonical)))] += 1
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'profiles.jsonl').write_text(''.join(
        canonical(dict(json.loads(profile), count=count)) + '\n'
        for profile, count in sorted(profiles.items())), encoding='utf-8')
    # Numeric/category summary only; no source paths, hashes, IDs or provenance logs.
    keys = ('policy_version', 'total_collected', 'total_successfully_classified',
            'expanded_total', 'core_industry_total', 'usable_requirements_jobs',
            'core_usable_requirements_jobs', 'strict_audit_approved', 'categories',
            'core_categories', 'scopes', 'multi_role', 'same_content_additional_ids')
    (destination / 'step7_summary.json').write_text(
        json.dumps({key: totals[key] for key in keys}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (destination / 'public_manifest.json').write_text(json.dumps(dict(
        format_version=1, dataset='Step 7 public research profiles',
        publication_date='2026-10-24', collection_start='2026-04-21',
        collection_end='2026-10-21', advertisements=len(jobs), profiles=len(profiles),
        source='Arbetsformedlingen JobTech JobSearch and Historical APIs',
        source_license='CC0', documentation='docs/public_research.md'), indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'data/processed/step7-expanded-20261024')
    parser.add_argument('--output', type=Path, default=DESTINATION)
    args = parser.parse_args()
    build(args.source, args.output)
