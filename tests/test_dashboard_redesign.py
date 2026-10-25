"""Presentation grouping and shared-filter regression coverage; no network calls."""
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from dashboard.presentation import CAREER_PATHS, OTHER_PATH, career_paths
from src.dashboard_data import load_dataset, filter_data, skill_counts

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'examples/public_research'

class RedesignTests(unittest.TestCase):
    def test_primary_partition_preserves_source_and_denominators(self):
        jobs, facts = load_dataset(PUBLIC)
        source = jobs.copy(deep=True)
        grouped = career_paths(jobs, 'primary_category_label')
        pd.testing.assert_frame_equal(jobs, source)
        self.assertEqual(len(grouped), 1778)
        self.assertEqual(grouped.groupby('career_path').advertisement_id.nunique().sum(), 1778)
        self.assertEqual(set(grouped.career_path), set(CAREER_PATHS) | {OTHER_PATH})
        self.assertTrue(grouped.loc[grouped.primary_category_label.eq('Unresolved primary category'), 'career_path'].eq(OTHER_PATH).all())
        empty, evidence = filter_data(grouped, facts, region=[], analysis_opportunity_types=['not_flagged_opportunity'])
        self.assertTrue(empty.empty)
        self.assertTrue(evidence.empty)
        self.assertEqual(list(empty.columns), list(grouped.columns))
        for path in grouped.career_path.unique():
            subset, evidence = filter_data(grouped, facts, career_path=[path], analysis_scope=['core_industry'])
            self.assertTrue(set(evidence.advertisement_id) <= set(subset.advertisement_id))
            counts = skill_counts(subset, evidence)
            self.assertTrue(counts.denominator_jobs.eq(len(subset)).all())
            self.assertTrue(counts.job_count.le(len(subset)).all())

    def test_shared_filters_reset_and_mode_switch_offline(self):
        with patch.dict('os.environ', {'JOBS_DASHBOARD_DATA': str(PUBLIC)}), patch('requests.sessions.Session.request', side_effect=AssertionError('Network forbidden')):
            app = AppTest.from_file(str(ROOT/'dashboard/app.py')).run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual([t.label for t in app.tabs], ['Overview','Skills & Technologies','Qualifications','Locations'])
            self.assertEqual(int(app.metric[3].value), 1111)
            app.multiselect(key='career_path').set_value(['Data Engineering']).run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            jobs, facts = load_dataset(PUBLIC)
            expected, _ = filter_data(career_paths(jobs, 'primary_category_label'), facts, career_path=['Data Engineering'], analysis_scope=['core_industry'])
            self.assertEqual(int(app.metric[3].value), len(expected))
            for item in app.get('plotly_chart'):
                spec = json.loads(item.proto.spec)
                for trace in spec['data']:
                    custom = trace.get('customdata', [])
                    if isinstance(custom, list):
                        self.assertTrue(all(row[2] <= len(expected) for row in custom))
            app.radio(key='chart_measure').set_value('Percent').run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            app.multiselect(key='region').set_value([]).run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual(int(app.metric[3].value), 0)
            next(b for b in app.button if b.label == 'Reset Filters').click().run(timeout=60)
            self.assertEqual(int(app.metric[3].value), 1111)
            app.selectbox(key='dataset_mode').set_value('Fictional demo').run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual(int(app.metric[3].value), 3)
            app.selectbox(key='dataset_mode').set_value('Research findings').run(timeout=60)
            self.assertFalse(app.exception, str(app.exception))
            self.assertEqual(int(app.metric[3].value), 1111)

if __name__ == '__main__':
    unittest.main()
