import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.distypes import TYPE_ORDER, TYPE_COLORS
from utils.filters import get_filtered_data
from utils.layout import format_num, PAGE_HELP_TEXT

# Set page
st.session_state["page"] = "metric"

# Check if disaster data is loaded
if "data" not in st.session_state:
    st.error('No disaster data available. Please check database connection.', icon="🚨")
else:
    data: pd.DataFrame = get_filtered_data()

    st.html("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 20px;
    }
    </style>
    """)

    # Table Header
    scol00, scol01, scol02, scol03, scol04 = st.columns(5, vertical_alignment="center")
    scol01.markdown('**N° Count**')
    scol02.markdown('**Total Deaths**')
    scol03.markdown('**Total Affected**')
    scol04.markdown("**Total Damage (USD Thousands)**")

    # Table Total Row
    scol10, scol11, scol12, scol13, scol14 = st.columns(5, vertical_alignment="center")
    scol10.markdown('**Total**')
    scol11.metric('N° Count', format_num(data['disno'].nunique()), label_visibility='collapsed')
    scol12.metric('Total Deaths', format_num(data['total_deaths'].sum()), label_visibility='collapsed')
    scol13.metric('Total Affected', format_num(data['total_affected'].sum()), label_visibility='collapsed')
    scol14.metric('Total Damage', format_num(data['total_damage_adjusted_usd_thousands'].sum()), label_visibility='collapsed')

    # Table Yearly Average Row
    scol20, scol21, scol22, scol23, scol24 = st.columns(5, vertical_alignment="center")
    scol20.markdown('**Yearly Average**')
    scol21.metric('N° Count', format_num(data.groupby('start_year')['disno'].nunique().mean()), label_visibility='collapsed')
    scol22.metric('Average Total Deaths', format_num(data.groupby('start_year')['total_deaths'].sum().mean()), label_visibility='collapsed')
    scol23.metric('Average Total Affected', format_num(data.groupby('start_year')['total_affected'].sum().mean()), label_visibility='collapsed')
    scol24.metric('Average Total Damage', format_num(data.groupby('start_year')['total_damage_adjusted_usd_thousands'].sum().mean()), label_visibility='collapsed')

    # Table Yearly Median Row
    scol30, scol31, scol32, scol33, scol34 = st.columns(5, vertical_alignment="center")
    scol30.markdown('**Yearly Median**')
    scol31.metric('N° Count', format_num(data.groupby('start_year')['disno'].nunique().median()), label_visibility='collapsed')
    scol32.metric('Median Total Deaths', format_num(data.groupby('start_year')['total_deaths'].sum().median()), label_visibility='collapsed')
    scol33.metric('Median Total Affected', format_num(data.groupby('start_year')['total_affected'].sum().median()), label_visibility='collapsed')
    scol34.metric('Median Total Damage', format_num(data.groupby('start_year')['total_damage_adjusted_usd_thousands'].sum().median()), label_visibility='collapsed')

    # Table Reporting %
    scol40, scol41, scol42, scol43, scol44 = st.columns(5, vertical_alignment="center")
    scol40.markdown('**Reporting %**')
    scol41.metric('N° Count', None, label_visibility='collapsed')
    scol42.metric('Reporting Deaths', format_num(data['total_deaths'].count() / len(data) * 100), label_visibility='collapsed')
    scol43.metric('Reporting Affected', format_num(data['total_affected'].count() / len(data) * 100), label_visibility='collapsed')
    scol44.metric('Reporting Damage', format_num(data['total_damage_adjusted_usd_thousands'].count() / len(data) * 100), label_visibility='collapsed')

    # Disaster Type Distribution Chart
    df = data.groupby('disaster_type').agg(
        count=('disaster_type', 'count'),
        death=('total_deaths', 'sum'),
        affected=('total_affected', 'sum'),
        damage=('total_damage_adjusted_usd_thousands', 'sum')
    ).reset_index()

    # Normalize to percent
    df['count'] = (df['count'] / df['count'].sum()) * 100
    df['death'] = (df['death'] / df['death'].sum()) * 100
    df['affected'] = (df['affected'] / df['affected'].sum()) * 100
    df['damage'] = (df['damage'] / df['damage'].sum()) * 100
    df = df.round(1)

    # Correct type ordering
    order = [i for i in TYPE_ORDER if i in df['disaster_type'].unique()][::-1]
    colors = [c for k, c in TYPE_COLORS.items() if k in df['disaster_type'].unique()][::-1]
    df = df.set_index('disaster_type').loc[order].reset_index()

    # Plot distribution
    fig = make_subplots(rows=1, cols=4, shared_yaxes=True, subplot_titles=("N° Count", "Total Deaths", "Total Affected", "Total Damage"))

    fig.add_trace(go.Bar(y=df['disaster_type'], x=df['count'], orientation='h', marker_color=colors, name='Count'), 1, 1)
    fig.add_trace(go.Bar(y=df['disaster_type'], x=df['death'], orientation='h', marker_color=colors, name='Deaths'), 1, 2)
    fig.add_trace(go.Bar(y=df['disaster_type'], x=df['affected'], orientation='h', marker_color=colors, name='Affected'), 1, 3)
    fig.add_trace(go.Bar(y=df['disaster_type'], x=df['damage'], orientation='h', marker_color=colors, name='Damage'), 1, 4)

    for i in range(1, 5):
        fig.update_xaxes(title_text='Percent %', row=1, col=i)

    fig.update_layout(
        title="Distribution per Disaster Type (%)",
        height=500 + 10 * len(df) ** 0.75,
        showlegend=False
    )
    fig.update_xaxes(range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)

    # Page Help
    with st.expander("See page details", expanded=False, icon=':material/info:'):
        st.markdown(PAGE_HELP_TEXT[st.session_state.page])
