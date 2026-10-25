"""Presentation-only groupings; source classifications are never rewritten."""
CAREER_PATHS = {
    'Data Engineering': ('Data Engineer', 'Data Warehouse / ETL Developer', 'Data Architect', 'Analytics Engineer'),
    'Data Science & Machine Learning': ('Data Scientist', 'ML Engineer', 'AI Engineer', 'AI / ML Research'),
    'Data Analytics': ('Data Analyst', 'BI Developer / BI Analyst'),
}
OTHER_PATH = 'Other & unassigned'


def career_paths(jobs, category_column):
    lookup = {category: path for path, categories in CAREER_PATHS.items() for category in categories}
    return jobs.assign(career_path=jobs[category_column].map(lookup).fillna(OTHER_PATH))


def readable(value):
    labels = {'core_industry': 'Core industry', 'academic_ai_ml_research': 'Academic research',
              'not_specified': 'Not specified', 'unspecified': 'Not specified',
              'alternative_required': 'Required alternative', 'mentioned_only': 'Merely mentioned',
              'not_flagged_opportunity': 'No opportunity flag'}
    return labels.get(str(value), str(value).replace('_', ' ').capitalize() if '_' in str(value) else str(value))
