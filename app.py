"""LogiSight FA-2: interactive last-mile delivery analytics."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from data_processing import prepare_data, filter_data, summaries, CATEGORIES

st.set_page_config(page_title='LogiSight | Delivery Analytics', page_icon='📦', layout='wide')
NAVY, TEAL, ORANGE = '#16324F', '#368C89', '#E99A47'
st.markdown('''<style>
.block-container{max-width:1500px;padding-top:2rem;padding-bottom:2rem}
h1,h2,h3{color:#16324F} [data-testid="stSidebar"]{background:#EDF6F6}
[data-testid="stMetric"]{background:#F4F8FA;border:1px solid #DFE9EF;border-radius:12px;padding:16px}
[data-testid="stMetricValue"]{color:#16324F} .hero{border-left:5px solid #368C89;padding:4px 20px;margin-bottom:24px}
.hero p{color:#607487;margin:4px 0} .hero h1{margin:0;padding:0;font-size:2.6rem}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_dataset(path, modified):
    return prepare_data(path)

path = Path(__file__).parent / 'data' / 'last_mile_delivery.csv'
if not path.exists():
    st.error('Dataset missing. Include data/last_mile_delivery.csv in your project.'); st.stop()
try:
    full, audit, threshold = load_dataset(str(path), path.stat().st_mtime_ns)
except (ValueError, OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
    st.error(f'Unable to load the dataset: {exc}'); st.stop()
if full.empty:
    st.error('No valid delivery records remain after cleaning.'); st.stop()

valid_dates = full['Order_Date'].dropna()
def reset_filters():
    for col in CATEGORIES: st.session_state['filter_' + col] = []
    st.session_state['use_dates'] = False
    for key in ['date_years', 'date_months', 'date_days']: st.session_state[key] = []
    if not valid_dates.empty:
        st.session_state['dates'] = (valid_dates.min().date(), valid_dates.max().date())

with st.sidebar:
    st.title('LogiSight')
    st.caption('DELIVERY ANALYTICS')
    st.divider()
    st.subheader('Explore deliveries')
    selections = {col: st.multiselect(col, sorted(full[col].unique().tolist()), key='filter_' + col, placeholder='All') for col in CATEGORIES}
    st.subheader('Date selection')
    st.caption('Leave a selection empty to include all available dates.')
    years = st.multiselect('Years', sorted(valid_dates.dt.year.unique().tolist()), key='date_years', placeholder='All years')
    import calendar
    months = st.multiselect('Months', list(range(1,13)), format_func=lambda n: calendar.month_name[n], key='date_months', placeholder='All months')
    days = st.multiselect('Days of month', list(range(1,32)), key='date_days', placeholder='All days')
    st.caption('Source dates: February–April 2022. Other months return no matching records.')
    use_dates = st.checkbox('Filter by order date', key='use_dates', disabled=valid_dates.empty)
    date_range = None
    if not valid_dates.empty:
        picked = st.date_input('Order date range', value=(valid_dates.min().date(), valid_dates.max().date()), key='dates')
        if use_dates:
            if len(picked) != 2:
                st.info('Select both a start and an end date.'); st.stop()
            date_range = picked
    st.button('Reset filters', on_click=reset_filters, use_container_width=True)
    st.caption('An empty category selection includes all values. Every chart uses the same filters.')
    st.divider()
    st.caption('FA-2 · Mathematics for AI-II')

filtered = filter_data(full, selections, date_range)
if years: filtered = filtered.loc[filtered.Order_Date.dt.year.isin(years)]
if months: filtered = filtered.loc[filtered.Order_Date.dt.month.isin(months)]
if days: filtered = filtered.loc[filtered.Order_Date.dt.day.isin(days)]
st.markdown('<div class="hero"><p>LOGISIGHT ANALYTICS</p><h1>Last Mile Delivery Dashboard</h1><p>Explore conditions, compare performance, and focus your next investigation.</p></div>', unsafe_allow_html=True)
st.caption(f'{len(filtered):,} of {len(full):,} cleaned records selected · {valid_dates.min():%d %b %Y} – {valid_dates.max():%d %b %Y}' if not valid_dates.empty else f'{len(filtered):,} selected records')
st.caption('Delivery times are shown in source units; the supplied CSV does not specify the unit.')
if filtered.empty:
    st.warning('No deliveries match these filters. Clear a selection or use Reset filters.'); st.stop()

for col, label, value in zip(st.columns(4), ['Delivery records', 'Average delivery time', 'Median delivery time', 'Late deliveries*'], [f'{len(filtered):,}', f'{filtered.Delivery_Time.mean():.2f}', f'{filtered.Delivery_Time.median():.2f}', f'{100*filtered.Late_Flag.mean():.2f}%']):
    col.metric(label, value)
st.caption(f'*Analytical late flag: delivery time > {threshold:.2f} (cleaned full-dataset mean + sample standard deviation). This is not a promised-deadline measure; the threshold stays fixed across filters.')

def style(fig):
    fig.update_layout(template='plotly_white', font=dict(color=NAVY, size=13), margin=dict(l=15,r=15,t=30,b=20), paper_bgcolor='rgba(0,0,0,0)', colorway=[TEAL, ORANGE, '#6483A0', '#B9A1CF'])
    return fig

def display(fig, key):
    st.plotly_chart(style(fig), use_container_width=True, key=key)

def bar(col, key, order=None):
    data = summaries(filtered, col)
    fig = px.bar(data, x=col, y='Average', hover_data={'Records':True,'Average':':.2f'}, text='Average', category_orders={col:order} if order else None, labels={'Average':'Average delivery time'}, color_discrete_sequence=[TEAL])
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_yaxes(rangemode='tozero')
    display(fig, key)

analytics, records, quality = st.tabs(['Performance insights', 'Delivery records', 'Data quality and method'])
with analytics:
    st.subheader('01 · Traffic and weather')
    st.caption('Compare average delivery times under the selected conditions. Hover to see record counts.')
    left, right = st.columns(2)
    with left: bar('Traffic','traffic',['Low','Medium','High','Jam','Unknown'])
    with right: bar('Weather','weather')
    st.subheader('02 · Vehicle comparison')
    vehicle = summaries(filtered,'Vehicle').sort_values('Average')
    display(px.bar(vehicle,x='Average',y='Vehicle',orientation='h',text='Average',hover_data={'Records':True,'Average':':.2f'},labels={'Average':'Average delivery time'},color_discrete_sequence=[TEAL]).update_traces(texttemplate='%{x:.2f}',textposition='outside').update_xaxes(rangemode='tozero'),'vehicle')
    small = vehicle.loc[vehicle.Records < 30,'Vehicle'].tolist()
    if small: st.caption('Small samples (fewer than 30 records): '+', '.join(small)+'. Interpret averages cautiously.')
    st.caption('Vehicle averages reflect different routes and conditions. Use Traffic and Area filters for a more comparable view.')
    st.subheader('03 · Agent performance')
    agents = filtered.dropna(subset=['Agent_Rating','Agent_Age'])
    if agents.empty:
        st.info('No valid ratings and ages are available for the selected records.')
    else:
        fig = px.scatter(agents,x='Agent_Rating',y='Delivery_Time',color='Age_Group',opacity=.25,render_mode='webgl',category_orders={'Age_Group':['Under 25','25–39','40 and above']},labels={'Agent_Rating':'Agent rating','Delivery_Time':'Delivery time','Age_Group':'Age group'},hover_data=['Order_ID','Vehicle','Area'])
        fig.update_traces(marker={'size':5})
        display(fig,'agents')
    st.caption('Age is not experience. These plots show associations, not proof of causes. Ratings outside the assumed 1–5 scale are excluded only from rating analysis.')
    st.subheader('04 · Area bottlenecks')
    st.caption('Area × traffic heatmap. Area represents a category, not a named geographic location. Empty cells have no records.')
    means = filtered.pivot_table(index='Area',columns='Traffic',values='Delivery_Time',aggfunc='mean',observed=True)
    counts = filtered.pivot_table(index='Area',columns='Traffic',values='Delivery_Time',aggfunc='size',observed=True).reindex(index=means.index,columns=means.columns).fillna(0)
    cols = [c for c in ['Low','Medium','High','Jam','Unknown'] if c in means.columns]
    means, counts = means[cols], counts[cols]
    fig = go.Figure(go.Heatmap(z=means.to_numpy(),x=means.columns.tolist(),y=means.index.tolist(),customdata=counts.to_numpy(),colorscale=[[0,'#E7F4F3'],[.5,TEAL],[1,ORANGE]],texttemplate='%{z:.1f}',hovertemplate='Area: %{y}<br>Traffic: %{x}<br>Average: %{z:.2f}<br>Records: %{customdata}<extra></extra>',colorbar={'title':'Average'}))
    fig.update_layout(xaxis_title='Traffic condition',yaxis_title='Area type')
    display(fig,'areas')
    st.subheader('05 · Product categories')
    ordered = filtered.groupby('Category')['Delivery_Time'].median().sort_values().index.tolist()
    display(px.box(filtered,x='Delivery_Time',y='Category',orientation='h',points=False,category_orders={'Category':ordered},labels={'Delivery_Time':'Delivery time'},color_discrete_sequence=[TEAL]).update_layout(height=max(450,35*len(ordered))),'categories')
    st.caption('Boxes show the middle 50% and median. Whiskers extend to observations within 1.5×IQR. Categories are ordered by median delivery time; all records are used.')
    st.subheader('Additional context')
    l,r = st.columns(2)
    with l:
        display(px.histogram(filtered,x='Delivery_Time',nbins=35,labels={'Delivery_Time':'Delivery time'},color_discrete_sequence=[TEAL]),'histogram')
    with r:
        daily = filtered.dropna(subset=['Order_Date']).groupby('Order_Date')['Delivery_Time'].agg(Average='mean',Records='size').reset_index()
        if not daily.empty:
            display(px.line(daily,x='Order_Date',y='Average',hover_data=['Records'],labels={'Order_Date':'Order date','Average':'Average delivery time'},color_discrete_sequence=[TEAL]),'trend')
        else: st.info('No valid order dates are available for a time trend.')
with records:
    st.subheader('Selected delivery records')
    st.download_button('Download filtered CSV',filtered.to_csv(index=False).encode('utf-8'),file_name='logisight_filtered_deliveries.csv',mime='text/csv')
    st.dataframe(filtered,use_container_width=True,hide_index=True)
    st.subheader('Group summaries')
    group = st.selectbox('Group by',CATEGORIES)
    st.dataframe(summaries(filtered,group),use_container_width=True,hide_index=True)
with quality:
    st.subheader('Cleaning audit')
    st.dataframe(pd.DataFrame(audit.items(),columns=['Check','Records or cells']),hide_index=True,use_container_width=True)
    st.markdown('''**Cleaning choices**
- Whitespace is trimmed and textual NaN/blank category values become Unknown.
- Orders with missing IDs or non-positive/non-numeric delivery times are removed. Duplicate IDs retain their first record.
- Metropolitan is displayed consistently by correcting the source label Metropolitian.
- Invalid dates remain in overall analysis but are excluded when a date filter is active.
- Ages outside 0–100 become missing. Missing ages remain in other analyses.
- A **1–5 rating scale is an explicit assumption**. Missing and out-of-range ratings (including 6.0) become missing for rating analysis; those deliveries remain in all other charts. Confirm this scale with the teacher/source.

**Metric definitions**
- Average and median use the selected valid delivery records.
- Late percentage = 100 × selected records above the fixed threshold ÷ selected records.
- Threshold uses the cleaned full-dataset mean plus sample standard deviation (ddof=1).
- Small samples can give unstable comparisons. No chart establishes a causal relationship.
- Data source: the supplied Last mile Delivery Data.csv. This is historical data, refreshed interactively when filters change.
''')
st.divider()
st.caption('LogiSight · Last Mile Delivery Analytics · FA-2')
