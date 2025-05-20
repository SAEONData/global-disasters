import plotly.graph_objects as go
import streamlit as st

from utils.filters import get_filtered_data
from utils.layout import generate_colorscale, PAGE_HELP_TEXT

SCOPES = ['world', 'africa', 'asia', 'europe', 'north america', 'south america']
COLORMAPS = [
    'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance', 'blackbody',
    'bluered', 'blues', 'blugrn', 'bluyl', 'brbg', 'brwnyl', 'bugn', 'bupu',
    'burg', 'burgyl', 'cividis', 'curl', 'darkmint', 'deep', 'delta', 'dense',
    'earth', 'edge', 'electric', 'emrld', 'fall', 'geyser', 'gnbu', 'gray',
    'greens', 'greys', 'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno',
    'jet', 'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
    'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl', 'piyg',
    'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor', 'purd',
    'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy', 'rdpu', 'rdylbu',
    'rdylgn', 'redor', 'reds', 'solar', 'spectral', 'speed', 'sunset',
    'sunsetdark', 'teal', 'tealgrn', 'tealrose', 'tempo', 'temps', 'thermal',
    'tropic', 'turbid', 'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu',
    'ylorbr', 'ylorrd'
]

VAR_DICT = {
    'count': 'N° Count',
    'death': 'Total Deaths',
    'affected': 'Total Affected',
    'damage': "Total Damage (USD Thousands)"
}
TITLE_DICT = {
    'count': 'Number of Disasters per Country',
    'death': 'Total Deaths per Country',
    'affected': 'Total Affected per Country',
    'damage': "Total Damage per Country (in Thousands USD)"
}

# Set current page
st.session_state["page"] = "map"

# Check if data is loaded
if "data" not in st.session_state:
    st.error('No disaster data available. Please check database connection.', icon="🚨")
else:
    data = get_filtered_data()

    # Data & period
    year_min = int(data['start_year'].min())
    year_max = int(data['end_year'].max())
    period = f"{year_min}-{year_max}" if year_min < year_max else f"{year_min}"

    if st.session_state.get('filter.country') is not None:
        st.error('Mapping tool cannot be set for one single country.', icon="🚨")
    else:
        # Controls
        row0_cols = st.columns(3, vertical_alignment="center")
        row1_cols = st.columns([1,1,1,3], vertical_alignment="center")
        variable = row0_cols[0].selectbox(
            "Impact Variable",
            VAR_DICT.keys(),
            format_func=lambda x: VAR_DICT.get(x)
        )
        scope = row0_cols[1].selectbox(
            "Zoom Options",
            SCOPES,
            format_func=lambda x: x.title()
        )
        aggregator = row0_cols[2].selectbox(
            'Aggregate by',
            ['Total', 'Yearly Average', 'Yearly Median']
        )
        custom = row1_cols[3].toggle('Custom Color Scale', value=False)
        land_color = row1_cols[0].color_picker('No Data', value='#dddddd')

        if not custom:
            cmap = row1_cols[1].selectbox(
                "Color Scale", COLORMAPS, index=COLORMAPS.index('amp')
            )
            reversed = row1_cols[2].toggle('Reversed Scale', value=True)
            if reversed:
                cmap += '_r'
        else:
            top_color = row1_cols[1].color_picker('Top Color', '#ba0c2f')
            bottom_color = row1_cols[2].color_picker('Bottom Color', '#ffffff')
            cmap = generate_colorscale(bottom_color, top_color)

        # Aggregate annually
        annual_data = data.groupby(
            ['country', 'region', 'iso', 'start_year']
        ).agg(
            count=('iso', 'count'),
            death=('total_deaths', 'sum'),
            affected=('total_affected', 'sum'),
            damage=('total_damage_adjusted_usd_thousands', 'sum')
        ).reset_index()

        if aggregator == 'Total':
            data_map = annual_data.groupby(['country', 'region', 'iso']).agg(
                count=('count', 'sum'),
                death=('death', 'sum'),
                affected=('affected', 'sum'),
                damage=('damage', 'sum')
            ).reset_index()
        elif aggregator == 'Yearly Average':
            data_map = annual_data.groupby(['country', 'region', 'iso']).agg(
                count=('count', 'mean'),
                death=('death', 'mean'),
                affected=('affected', 'mean'),
                damage=('damage', 'mean')
            ).reset_index()
        elif aggregator == 'Yearly Median':
            data_map = annual_data.groupby(['country', 'region', 'iso']).agg(
                count=('count', 'median'),
                death=('death', 'median'),
                affected=('affected', 'median'),
                damage=('damage', 'median')
            ).reset_index()

        # Map Plot
        fig = go.Figure(
            data=go.Choropleth(
                locations=data_map["iso"],
                z=data_map[variable],
                text=data_map["country"],
                colorscale=cmap,
                autocolorscale=False,
                reversescale=True,
                marker_line_color='darkgray',
                marker_line_width=.5,
            )
        )

        fig.update_geos(
            resolution=50,
            showland=True,
            landcolor=land_color,
        )
        fig.update_layout(
            title={
                'automargin': True,
                'text': f'{TITLE_DICT.get(variable)} ({period} {aggregator})',
                'font': {
                    'family': 'Arial',
                    'size': 24
                }
            },
            height=600,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular',
                scope=scope
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Page Help
        with st.expander("See page details", expanded=False, icon=':material/info:'):
            st.markdown(PAGE_HELP_TEXT[st.session_state.page])
