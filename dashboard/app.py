"""Read-only, offline Swedish Data & AI research explorer."""
import json
import os
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.presentation import CAREER_PATHS, OTHER_PATH, career_paths, readable
from src.dashboard_data import (PERIOD, REQUESTED, SKILLS, count_ads, coverage,
    dashboard_dataset, dataset_files, filter_data, language_counts, load_dataset, skill_counts)

st.set_page_config(page_title='Swedish Data & AI | Market Observatory', page_icon='🇸🇪', layout='wide')
st.markdown('''<style>
.stApp {color:#14243b} h1,h2,h3 {letter-spacing:-.035em}
h1 {font-weight:750;font-size:clamp(2rem,3vw,2.8rem)} .observatory-label {color:#167d9a;font-size:.78rem;font-weight:700;letter-spacing:.16em}
[data-testid="stMetric"] {background:white;border:1px solid #dfe7ef;border-radius:12px;padding:16px}
[data-testid="stSidebar"] {border-right:1px solid #dfe7ef}
@media(max-width:700px) {h1 {font-size:2rem} [data-testid="stMetric"] {padding:10px}}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def read_data(path, versions):
    return load_dataset(path)

@st.cache_data(show_spinner=False)
def read_json(path, version):
    return json.loads(Path(path).read_text(encoding='utf-8'))

mode = st.sidebar.selectbox('Dataset', ['Research findings', 'Fictional demo'], key='dataset_mode')
directory = dashboard_dataset(ROOT / 'data/processed', os.environ.get('JOBS_DASHBOARD_DATA')) if mode == 'Research findings' else ROOT / 'examples/demo_dataset'
is_public = (directory / 'public_manifest.json').is_file()
if not all((directory / name).is_file() for name in dataset_files(directory)):
    st.error('Dashboard data is unavailable. Set JOBS_DASHBOARD_DATA to a completed publication directory, or use examples/demo_dataset for the fictional demo. See README.md.')
    st.stop()
try:
    all_jobs, all_facts = read_data(str(directory), tuple((directory / name).stat().st_mtime_ns for name in dataset_files(directory)))
except (OSError, ValueError, KeyError):
    st.error('The selected dataset is incomplete, unreadable, or invalid. Choose a completed publication or examples/demo_dataset.')
    st.stop()
is_demo = (directory / 'demo_manifest.json').exists()
expanded = (directory / 'step7_summary.json').exists()
category_column = 'primary_category_label' if expanded else 'ai_primary_category'
scope_column = 'analysis_scope' if expanded else 'reporting_scope'
all_jobs = career_paths(all_jobs, category_column)

# Clear filter state before creating widgets, including on dataset changes.
filter_keys = ['career_path', category_column, scope_column, 'region', 'seniority', 'inclusion_quality',
               'ai_scope', 'analysis_opportunity_types', 'opportunity_group', 'multi_role_group', 'inclusion_method']
if st.session_state.get('_dataset') != str(directory):
    for key in filter_keys:
        st.session_state.pop(key, None)
    st.session_state['_dataset'] = str(directory)
def reset_filters():
    for key in filter_keys:
        st.session_state.pop(key, None)

with st.sidebar:
    st.markdown('### Refine the view')
    st.button('Reset Filters', on_click=reset_filters, width='stretch')
    filters = {}
    for label, column in [('Career path', 'career_path'), ('Detailed job category', category_column),
                          ('Region', 'region'), ('Job scope', scope_column), ('Seniority', 'seniority')]:
        options = sorted(all_jobs[column].fillna('not_specified').replace('', 'not_specified').unique().tolist())
        default = ['core_industry'] if column == scope_column and 'core_industry' in options else ['__all__']
        values = st.multiselect(label, ['__all__'] + options, default=default,
            format_func=lambda value: 'All' if value == '__all__' else readable(value), key=column)
        filters[column] = None if '__all__' in values else values
    if expanded:
        quality = st.selectbox('Audit quality', ['All accepted AI-relevant jobs', 'Audit-approved only'], key='inclusion_quality')
        filters['strict_audit_approved'] = [True] if quality == 'Audit-approved only' else None
        with st.expander('Scope & opportunity details'):
            for label, column in [('Saved AI scope', 'ai_scope'), ('Opportunity status', 'opportunity_group'), ('Multi-role advertisements', 'multi_role_group')]:
                options = sorted(all_jobs[column].fillna('not_specified').replace('', 'not_specified').unique().tolist())
                values = st.multiselect(label, ['__all__'] + options, default=['__all__'],
                    format_func=lambda value: 'All' if value == '__all__' else readable(value), key=column)
                filters[column] = None if '__all__' in values else values
            types = sorted({kind for types in all_jobs.analysis_opportunity_types for kind in (types or ['not_flagged_opportunity'])})
            values = st.multiselect('Opportunity type', ['__all__'] + types, default=['__all__'],
                format_func=lambda value: 'All' if value == '__all__' else readable(value), key='analysis_opportunity_types')
            filters['analysis_opportunity_types'] = None if '__all__' in values else values
    if not expanded and 'inclusion_method' in all_jobs:
        options = sorted(all_jobs.inclusion_method.unique().tolist())
        values = st.multiselect('Inclusion method', ['__all__'] + options, default=['__all__'],
            format_func=lambda value: 'All' if value == '__all__' else readable(value), key='inclusion_method')
        filters['inclusion_method'] = None if '__all__' in values else values
    st.caption('Remove All to choose specific values. Empty selections return no advertisements. Career paths use primary categories only.')

jobs, facts = filter_data(all_jobs, all_facts, **filters)
n = len(jobs)
requested = facts[facts.modality.isin(REQUESTED)]
st.markdown('<div class="observatory-label">SWEDISH DATA & AI · MARKET OBSERVATORY</div>', unsafe_allow_html=True)
st.title('Explore the paths. Understand the skills.')
st.caption(f'Research collection · {PERIOD} · Distinct advertisements, with evidence-aware analytics')
if is_public:
    st.info(f'PUBLIC RESEARCH SNAPSHOT · {len(all_jobs):,} relevant advertisements. Original advertisements and source evidence are private.')
if is_demo:
    st.warning('FICTIONAL DEMO · Six handwritten examples. All classifications, counts and audit states are synthetic.')
active = []
for column, values in filters.items():
    if values is None:
        continue
    if column == 'strict_audit_approved':
        active.append('Audit-approved only')
    elif column == 'analysis_opportunity_types':
        if len(values) != len(types): active.append('Opportunity: ' + ', '.join(map(readable, values)))
    elif len(values) != all_jobs[column].fillna('not_specified').replace('', 'not_specified').nunique():
        active.append(readable(column) + ': ' + (', '.join(map(readable, values)) or 'None'))
st.caption('Active filters · ' + (' · '.join(active) if active else 'All accepted advertisements'))

summary_path = directory / ('step7_summary.json' if expanded else 'step6_summary.json')
totals = read_json(str(summary_path), summary_path.stat().st_mtime_ns) if summary_path.exists() else {}
columns = st.columns(4)
for column, label, value in zip(columns,
    ['Collected advertisements', 'Successfully classified', 'AI-relevant advertisements', 'Current selection'],
    [totals.get('total_collected', 'Unavailable'), totals.get('total_successfully_classified', 'Unavailable'), len(all_jobs), n]):
    column.metric(label, value)
st.caption('First three totals describe the dataset; current selection reflects every active filter.' if not is_demo else 'All totals above describe fictional examples; no real AI classifications were performed.')

if not n:
    st.warning('No advertisements match. Broaden your selection or use Reset Filters in the sidebar.')
    st.stop()

measure = st.radio('Chart measure', ['Advertisements', 'Percent'], horizontal=True, key='chart_measure')
metric = 'percent' if measure == 'Percent' else 'job_count'
COLORS = ['#167d9a', '#203c61', '#63a99b', '#8192aa', '#b2bac6']

def chart(frame, label, title, color=None):
    st.markdown('#### ' + title)
    if frame.empty:
        st.caption('No matching evidence in this selection.')
        return
    if len(frame) > 15:
        st.caption('Showing leading groups; searchable tables and evidence retain the full selection.')
    if color:
        top_labels = frame.groupby(label).job_count.sum().nlargest(10).index
        frame = frame[frame[label].isin(top_labels)].copy()
    else:
        frame = frame.head(15).copy()
    frame[label] = frame[label].map(readable)
    if color: frame[color] = frame[color].map(readable)
    fig = px.bar(frame, x=metric, y=label, orientation='h', color=color,
                 text=metric, custom_data=['job_count', 'percent', 'denominator_jobs'],
                 color_discrete_sequence=COLORS, barmode='group')
    fig.update_traces(texttemplate='%{x:.1f}%' if metric == 'percent' else '%{x:,}',
        textposition='auto', cliponaxis=False,
        hovertemplate='%{y}<br>%{customdata[0]:,} advertisements<br>%{customdata[1]:.1f}% of %{customdata[2]:,}<extra></extra>')
    fig.update_layout(template='plotly_white', height=max(260, 48 * frame[label].nunique() + 60),
        margin=dict(l=0, r=25, t=8, b=10), font=dict(family='Arial, sans-serif', color='#203c61'),
        yaxis=dict(autorange='reversed', title=None, categoryorder='array', categoryarray=frame[label].drop_duplicates().tolist(),
            tickmode='array', tickvals=frame[label].drop_duplicates().tolist(),
            ticktext=['<br>'.join(textwrap.wrap(value, 24)) for value in frame[label].drop_duplicates()]),
        xaxis=dict(title='Share of selected advertisements (%)' if metric == 'percent' else 'Distinct advertisements', gridcolor='#edf1f5', zeroline=False),
        legend=dict(title=None, orientation='h', y=1.15), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, key='chart_' + title, width='stretch', config={'displayModeBar': False, 'responsive': True})

def table(frame, key):
    search = st.text_input('Search table', key=key, placeholder='Type to filter rows…')
    if search:
        frame = frame[frame.astype(str).apply(lambda col: col.str.contains(search, case=False, regex=False)).any(axis=1)]
    frame = frame.copy()
    for column in ['modality', 'kind', 'seniority', 'analysis_scope', 'reporting_scope', 'requirement_type', 'swedish_requirement', 'english_requirement', 'bound_type']:
        if column in frame:
            frame[column] = frame[column].map(readable)
    frame.columns = [readable(c) for c in frame.columns]
    st.dataframe(frame, hide_index=True, width='stretch')

st.caption(f'Chart denominator: {n:,} selected advertisements. Overlapping skills and evidence strengths may exceed 100% when added.')
overview, skills, qualifications, geography = st.tabs(['Overview', 'Skills & Technologies', 'Qualifications', 'Locations'])
with overview:
    cards = st.columns(3)
    for col, path in zip(cards, CAREER_PATHS):
        subset = jobs[jobs.career_path.eq(path)]
        with col:
            with st.container(border=True):
                st.markdown('#### ' + path)
                st.metric('Advertisements', len(subset))
                st.caption(f'{len(subset)/n:.1%} of selection')
                st.caption(' · '.join(CAREER_PATHS[path]))
    other = int(jobs.career_path.eq(OTHER_PATH).sum())
    st.caption(f'Other & unassigned: {other:,} advertisements. Detailed classifications and occupation scopes are retained below.')
    a,b = st.columns([1.4,1])
    with a: chart(count_ads(jobs, 'career_path', n), 'career_path', 'Career-path distribution')
    with b: chart(count_ads(jobs, scope_column, n), scope_column, 'Occupation scope')
    st.markdown('#### Selection at a glance')
    a,b,c = st.columns(3)
    a.metric('Usable requirements evidence', int(jobs.requirements_data_usable.eq(True).sum()), help='Jobs with qualified skill, language, education or professional-experience evidence.')
    b.metric('With requested skills', requested.loc[requested.kind.isin(SKILLS), 'advertisement_id'].nunique())
    c.metric('Regions represented', jobs.region.replace('', pd.NA).nunique())
    top = skill_counts(jobs, facts)
    if not top.empty:
        st.caption(f"Most frequent requested skill: {top.iloc[0]['value']} · {top.iloc[0]['job_count']:,} advertisements ({top.iloc[0]['percent']:.1f}% of selection). Required, preferred and required alternatives combined.")
    with st.expander('Detailed categories & evidence coverage'):
        chart(count_ads(jobs, category_column, n), category_column, 'Primary job categories')
        table(coverage(jobs, facts), 'coverage_search')
with skills:
    choices = {'Required': 'required', 'Preferred': 'preferred', 'Required alternative': 'alternative_required', 'Merely mentioned': 'mentioned_only', 'Ambiguous mention': 'ambiguous'}
    selected = st.multiselect('Evidence strength', list(choices), default=['Required', 'Preferred', 'Required alternative'])
    modalities = [choices[x] for x in selected]
    st.caption('Required alternatives are choices, not individually mandatory skills. Mentions and ambiguous evidence are never labeled as requirements.')
    a,b = st.columns(2)
    with a: chart(skill_counts(jobs, facts, ('programming_language',), modalities), 'value', 'Programming languages')
    with b: chart(skill_counts(jobs, facts, ('cloud_platform',), modalities), 'value', 'Cloud platforms')
    chart(skill_counts(jobs, facts, ('data_tool',), modalities), 'value', 'Data tools & technologies')
    st.markdown('#### Compare career paths')
    values = sorted(facts.loc[facts.kind.isin(SKILLS), 'value'].unique())
    if values:
        value = st.selectbox('Technology', values)
        rows = []
        for path, group in jobs.groupby('career_path'):
            ids = facts.loc[facts.value.eq(value) & facts.kind.isin(SKILLS) & facts.modality.isin(modalities), 'advertisement_id']
            count = group.loc[group.advertisement_id.isin(ids), 'advertisement_id'].nunique()
            rows.append(dict(career_path=path, job_count=count, denominator_jobs=len(group), percent=100*count/len(group)))
        chart(pd.DataFrame(rows).sort_values('job_count', ascending=False), 'career_path', f'{value} by career path')
        st.caption('Each comparison percentage uses the selected advertisements within that career path.')
    with st.expander('Evidence-strength detail'):
        table(count_ads(facts[facts.kind.isin(SKILLS) & facts.modality.isin(modalities)], ['kind','value','modality'], n), 'skill_search')
with qualifications:
    a,b = st.columns(2)
    with a: chart(language_counts(jobs, 'swedish'), 'swedish_requirement', 'Swedish')
    with b: chart(language_counts(jobs, 'english'), 'english_requirement', 'English')
    st.caption('Not specified means insufficient or conflicting evidence. It does not mean the language is not required.')
    a,b = st.columns(2)
    with a: chart(count_ads(requested[requested.kind.eq('education')], ['value','modality'], n), 'value', 'Education', 'modality')
    with b: chart(count_ads(jobs, 'seniority', n), 'seniority', 'Explicit seniority')
    st.markdown('#### Professional experience')
    exp = requested[requested.kind.eq('experience')]
    st.caption(f'{exp.advertisement_id.nunique():,} of {n:,} advertisements have explicit requested years. Years are never inferred from seniority or study duration.')
    if exp.empty: st.caption('No explicit experience-years evidence in this selection.')
    else: table(count_ads(exp, ['stated_years','minimum_years','maximum_years','bound_type','modality'], n), 'experience_search')
with geography:
    chart(count_ads(jobs.assign(region=jobs.region.fillna('not_specified').replace('', 'not_specified')), 'region', n), 'region', 'Advertisements by region')
    st.caption('Use the Region filter to compare a local subset across all four sections. Source locations are retained without inferred coordinates.')
    regional = count_ads(jobs, ['region','career_path'], n)
    chart(regional, 'region', 'Regional career-path mix', 'career_path')
    with st.expander('Municipalities & work arrangements'):
        table(count_ads(jobs, 'municipality', n), 'municipality_search')
        table(count_ads(facts[facts.kind.isin(['employment_type','working_time','work_arrangement'])], ['kind','value'], n), 'arrangement_search')

with st.expander('About / Methodology'):
    st.write('AI classifications are provisional and have not been independently verified. This accepted analyzed subset is not representative of whole-market demand. Missing evidence does not mean a requirement is absent. Advertisements may include repeated postings.')
    st.write('Career paths group primary categories only; secondary categories never add counting units. Academic, governance, adjacent and opportunity scopes remain separately filterable. Opportunity reporting scope takes precedence over academic scope; saved AI scope retains overlaps.')
    st.write('Requirement charts use all selected advertisements as denominator, including those without usable evidence. Career-path comparisons explicitly use within-path denominators. Required alternatives and preferences are distinct from mandatory requirements; mere mentions are separate.')
    with st.expander('Processing decisions for all collected advertisements'):
        st.json(totals)
        coverage_file = directory / 'corpus_coverage.csv'
        if not is_public and coverage_file.exists():
            st.download_button('Download processing status for every collected ID', coverage_file.read_bytes(), 'corpus_coverage.csv', 'text/csv')
    for name in ['policy_activation.json', 'automatic_duties_summary.json']:
        path = directory / name
        if path.exists():
            st.write(readable(path.stem))
            st.json(read_json(str(path), path.stat().st_mtime_ns))
    st.caption('Public profiles contain no original advertisement text, titles, employers, source IDs or excerpts. See docs/public_research.md for the full methodology.')
evidence = st.expander('Explore data & supporting evidence')
with evidence:
    if is_public:
        st.subheader('Public research data')
        st.write('Original advertisements and evidence are withheld. Internal profile-unit IDs are counting units, not source identifiers. All statistical charts and filters retain their original denominators.')
        st.download_button('Download counted statistical profiles', (directory / 'profiles.jsonl').read_bytes(), 'profiles.jsonl', 'application/x-ndjson')
    else:
        st.subheader('Inspect the advertisements behind a statistic')
        stat = st.selectbox('Restrict to evidence value', ['All advertisements'] + sorted(facts.value.unique().tolist()))
        candidate = jobs if stat == 'All advertisements' else jobs[jobs.advertisement_id.isin(facts.loc[facts.value.eq(stat), 'advertisement_id'])]
        tablecols = ['advertisement_id', 'job_title', 'ai_primary_category', 'reporting_scope', 'region', 'seniority', 'swedish_requirement', 'english_requirement', 'education_level', 'requirements_data_usable']
        tablecols += [c for c in ['inclusion_method', 'inclusion_policy_version', 'dashboard_inclusion_policy_version', 'analysis_scope', 'analysis_opportunity_types', 'multi_role_group', 'strict_audit_approved', 'v3_audit_status'] if c in candidate.columns]
        table(candidate[tablecols], 'job_search')
        st.download_button('Download filtered job table', candidate[tablecols].to_csv(index=False).encode('utf-8-sig'), 'filtered_jobs.csv', 'text/csv')
        if not candidate.empty:
            labels = dict(zip(candidate.advertisement_id, candidate.job_title))
            identifier = st.selectbox('Open original job and supporting evidence', candidate.advertisement_id.tolist(), format_func=lambda x: f'{x} · {labels[x]}')
            job = candidate.set_index('advertisement_id').loc[identifier]
            st.markdown('**' + job.job_title + '**')
            st.caption(f'{job.employer} · {job.region} · Published {job.publication_date}')
            st.write('Classification:', job.ai_primary_category, '· Scope:', job.reporting_scope)
            st.write('Classification provenance:', job.classification_selected_run)
            if 'inclusion_method' in job.index:
                st.write('Inclusion:', job.inclusion_method, ' / ', job.inclusion_policy_version)
                duty_evidence = job.get('inclusion_duties_evidence')
                if isinstance(duty_evidence, list):
                    with st.expander('Automatic duties audit evidence'):
                        st.dataframe(pd.DataFrame(duty_evidence), hide_index=True, width='stretch')
            if expanded:
                st.write('Step 7 inclusion:', job.dashboard_inclusion_method, ' / ', job.dashboard_inclusion_policy_version)
                st.write('Historical v3 audit:', job.v3_audit_status, job.v3_audit_reasons)
                st.json(dict(model=job.get('ai_model'), prompt_version=job.get('ai_prompt_version'), saved_source_evidence=job.get('ai_evidence'), saved_source_spans=job.get('ai_evidence_spans')))
            st.write('Original AI scope:', job.get('ai_scope') or job.get('ai_role_scope') or 'Not supplied by legacy classifier')
            st.write('AI reasoning:', job.get('ai_reasoning', ''))
            url = str(job.get('original_advertisement_url', ''))
            if url.startswith(('https://', 'http://')): st.link_button('Open source advertisement', url)
            with st.expander('Full original description', expanded=False): st.text(job.description_text)
            st.caption('Offsets are Python Unicode character offsets [start, end) in the original source field. Context-heading offsets are retained in the downloadable evidence table.')
            evidence_rows = facts[facts.advertisement_id.eq(identifier)]
            st.dataframe(evidence_rows[['kind', 'value', 'modality', 'source_field', 'evidence_start', 'evidence_end', 'evidence_text']], hide_index=True, width='stretch')
            st.download_button('Download full evidence for this job', evidence_rows.to_csv(index=False).encode('utf-8-sig'), f'evidence_{identifier}.csv', 'text/csv')
st.caption('Offline research explorer · No API requests · Advertisements, not unique vacancies or whole-market demand.')
