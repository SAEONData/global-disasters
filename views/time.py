import plotly.express as px
import streamlit as st

from utils.distypes import TYPE_ORDER, TYPE_COLORS
from utils.filters import get_filtered_data
from utils.layout import PAGE_HELP_TEXT

VAR_DICT = {
    'count': 'N° Count',
    'death': 'Total Deaths',
    'affected': 'Total Affected',
    'damage': "Total Damage (USD Thousands)"
}

# Set current page
st.session_state["page"] = "time"

# Check if data is loaded
if "data" not in st.session_state:
    st.error('No disaster data available. Please check database connection.', icon="🚨")
else:
    data = get_filtered_data()

    cols = st.columns(2)
    variable = cols[0].selectbox(
        "Impact Variable",
        VAR_DICT.keys(),
        format_func=lambda x: VAR_DICT.get(x)
    )
    stacker = cols[1].selectbox(
        "Stack by",
        [None, 'Types', 'Regions', 'Subregions']
    )

    if stacker is None:
        data_time = data.groupby(['start_year']).agg(
            count=('disno', 'count'),
            death=('total_deaths', 'sum'),
            affected=('total_affected', 'sum'),
            damage=('total_damage_adjusted_usd_thousands', 'sum')
        ).reset_index()

        fig = px.bar(data_time, x='start_year', y=variable)
        fig.update_traces(marker_color='#214B8C')

    elif stacker == 'Types':
        data_time = data.groupby(['start_year', 'disaster_type']).agg(
            count=('disno', 'count'),
            death=('total_deaths', 'sum'),
            affected=('total_affected', 'sum'),
            damage=('total_damage_adjusted_usd_thousands', 'sum')
        ).reset_index()

        order = [i for i in TYPE_ORDER if i in data_time['disaster_type'].unique()]
        fig = px.bar(
            data_time,
            x='start_year',
            y=variable,
            color='disaster_type',
            category_orders={'disaster_type': order}
        )
        fig.for_each_trace(lambda t: t.update(marker_color=TYPE_COLORS.get(t.name, '#214B8C')))

    elif stacker == 'Regions':
        data_time = data.groupby(['start_year', 'region']).agg(
            count=('disno', 'count'),
            death=('total_deaths', 'sum'),
            affected=('total_affected', 'sum'),
            damage=('total_damage_adjusted_usd_thousands', 'sum')
        ).reset_index()

        fig = px.bar(
            data_time,
            x='start_year',
            y=variable,
            color='region'
        )

    elif stacker == 'Subregions':
        data_time = data.groupby(['start_year', 'subregion']).agg(
            count=('disno', 'count'),
            death=('total_deaths', 'sum'),
            affected=('total_affected', 'sum'),
            damage=('total_damage_adjusted_usd_thousands', 'sum')
        ).reset_index()

        fig = px.bar(
            data_time,
            x='start_year',
            y=variable,
            color='subregion'
        )

    # Final figure layout
    fig.update_layout(
        yaxis_title=VAR_DICT[variable]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Page Help
    with st.expander("See page details", expanded=False, icon=':material/info:'):
        st.markdown(PAGE_HELP_TEXT[st.session_state.page])
