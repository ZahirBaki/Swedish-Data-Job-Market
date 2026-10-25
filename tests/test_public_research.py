"""Public schema, offline clone launch and optional exact private-data parity."""
import json
import os
from pathlib import Path
import shutil
import socket
from contextlib import contextmanager
import uuid
import unittest
from unittest.mock import patch

from src.dashboard_data import (REQUESTED, SKILLS, count_ads, coverage,
                                filter_data, language_counts, load_dataset, skill_counts)
from tools.build_public_research import (DESTINATION, FACT_FIELDS, JOB_FIELDS,
                                         KINDS, ROOT, build)

@contextmanager
def temporary_directory():
    path = ROOT / 'tests' / ('.test-public-' + uuid.uuid4().hex)
    path.mkdir()
    try:
        yield str(path)
    finally:
        assert path.resolve().is_relative_to((ROOT / 'tests').resolve())
        shutil.rmtree(path)


PRIVATE = ROOT / 'data/processed/step7-expanded-20261024'


def normalize(frame):
    return sorted(json.dumps(row, sort_keys=True, default=str) for row in
                  frame.to_dict('records'))


def statistics(jobs, facts):
    n = len(jobs)
    requested = facts[facts.modality.isin(REQUESTED)]
    result = [n, int(jobs.strict_audit_approved.sum()),
              int(jobs.requirements_data_usable.sum()), normalize(coverage(jobs, facts))]
    for column in ['primary_category_label', 'analysis_scope', 'seniority', 'region', 'municipality']:
        result.append(normalize(count_ads(jobs, column, n)))
    for language in ['swedish', 'english']:
        result.append(normalize(language_counts(jobs, language)))
    for modality in [REQUESTED, ('required',), ('preferred',), ('alternative_required',),
                     ('mentioned_only',), ('ambiguous',)]:
        result.append(normalize(skill_counts(jobs, facts, modalities=modality)))
        selected = facts[facts.kind.isin(SKILLS) & facts.modality.isin(modality)]
        result.append(normalize(count_ads(selected, ['kind', 'value', 'modality'], n)))
    result.append(normalize(count_ads(requested[requested.kind.eq('education')], ['value', 'modality'], n)))
    result.append(normalize(count_ads(requested[requested.kind.eq('experience')],
                                     ['stated_years', 'minimum_years', 'maximum_years', 'bound_type', 'modality'], n)))
    result.append(normalize(count_ads(facts[facts.kind.isin(['employment_type', 'working_time', 'work_arrangement'])], ['kind', 'value'], n)))
    return result


class PublicResearchTests(unittest.TestCase):
    def test_schema_and_totals(self):
        jobs, facts = load_dataset(DESTINATION)
        self.assertEqual(len(jobs), 1778)
        self.assertEqual(int(jobs.requirements_data_usable.sum()), 1035)
        self.assertEqual(int(jobs.strict_audit_approved.sum()), 214)
        core, _ = filter_data(jobs, facts, analysis_scope=['core_industry'])
        self.assertEqual(len(core), 1111)
        self.assertEqual(int(core.requirements_data_usable.sum()), 611)
        for line in (DESTINATION/'profiles.jsonl').read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            self.assertEqual(set(row), {'attributes', 'facts', 'count'})
            self.assertEqual(set(row['attributes']), set(JOB_FIELDS))
            for fact in row['facts']:
                self.assertEqual(set(fact), set(FACT_FIELDS))
                self.assertIn(fact['kind'], KINDS)

    @unittest.skipUnless(PRIVATE.exists(), 'Optional private-source parity')
    def test_all_charts_and_filter_partitions_match_original(self):
        original = load_dataset(PRIVATE)
        public = load_dataset(DESTINATION)
        selections = [{}]
        for column in ['analysis_scope', 'ai_scope', 'opportunity_group', 'multi_role_group',
                       'strict_audit_approved', 'primary_category_label', 'region', 'seniority']:
            for value in original[0][column].dropna().unique():
                selections.append({column: [value]})
        for value in sorted({v for row in original[0].analysis_opportunity_types for v in row}):
            selections.append({'analysis_opportunity_types': [value]})
        selections += [{'analysis_scope': ['core_industry'], 'strict_audit_approved': [True]},
                       {'analysis_scope': []}]
        for selection in selections:
            with self.subTest(selection=selection):
                self.assertEqual(statistics(*filter_data(*original, **selection)),
                                 statistics(*filter_data(*public, **selection)))
        # Exact public projection equality proves arbitrary joint-filter parity too.
        with temporary_directory() as temp:
            build(PRIVATE, Path(temp))
            for name in ['profiles.jsonl', 'public_manifest.json', 'step7_summary.json']:
                self.assertEqual((Path(temp)/name).read_bytes(), (DESTINATION/name).read_bytes())

    def test_fresh_public_copy_without_credentials_or_network(self):
        from streamlit.testing.v1 import AppTest
        with temporary_directory() as temp:
            clone = Path(temp)
            for name in ['src', 'dashboard', 'examples']:
                shutil.copytree(ROOT/name, clone/name, ignore=shutil.ignore_patterns('__pycache__'))
            self.assertFalse((clone/'data').exists())
            real_connect = socket.socket.connect
            def connect(sock, address):
                if isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1'):
                    return real_connect(sock, address)
                raise AssertionError('External network forbidden')
            # Clear every credential and override; forbid socket and HTTP connections.
            with patch.dict('os.environ', {key: value for key, value in os.environ.items() if key in ('SYSTEMROOT', 'WINDIR', 'USERPROFILE', 'HOME', 'HOMEDRIVE', 'HOMEPATH', 'TEMP', 'TMP', 'PATH')}, clear=True), \
                 patch('socket.socket.connect', new=connect), \
                 patch('src.dashboard_data.__file__', str(clone/'src/dashboard_data.py')), \
                 patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP forbidden')):
                app = AppTest.from_file(str(clone/'dashboard/app.py')).run(timeout=60)
                self.assertFalse(app.exception, str(app.exception))
                self.assertFalse(app.error)
                self.assertEqual([int(item.value) for item in app.metric[:4]], [5023, 3138, 1778, 1111])
                self.assertTrue(any('PUBLIC RESEARCH SNAPSHOT' in item.value for item in app.info))
                app.selectbox(key='inclusion_quality').set_value('Audit-approved only').run(timeout=60)
                self.assertFalse(app.exception, str(app.exception))
                app.selectbox(key='dataset_mode').set_value('Fictional demo').run(timeout=60)
                self.assertFalse(app.exception, str(app.exception))
                self.assertTrue(any('FICTIONAL DEMO' in item.value for item in app.warning))


if __name__ == '__main__':
    unittest.main()
