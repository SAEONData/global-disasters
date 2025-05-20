import pandas as pd
import streamlit as st

DOC_URI = "https://doc.emdat.be/docs"
CLASSIF_KEY_DOC_URI = (
    f"{DOC_URI}/data-structure-and-content/disaster-classification-system/"
    f"#main-classification-tree"
)

def init_sidebar_filters() -> None:
    """Initialize sidebar filters."""
    ss = st.session_state

    # If no data, disable filters
    filters_disabled = "data" not in ss

    if not filters_disabled:
        if "filter.disabled" not in ss:
            set_filters_to_default()

        col1, col2 = st.sidebar.columns(2)

        col1.number_input(
            label='**Start year**',
            min_value=ss["filter.year_min"],
            max_value=ss["filter.year_max"],
            key='filter.start'
        )

        col2.number_input(
            label='**End year**',
            min_value=ss["filter.year_min"],
            max_value=ss["filter.year_max"],
            key='filter.end'
        )

        st.sidebar.text_input(
            label="**Classification Key**",
            key="filter.classification_key",
            help="Enter the key or its initial part to filter"
        )
        st.sidebar.caption(
            f"_Check classification keys [here]({CLASSIF_KEY_DOC_URI})._"
        )

        st.sidebar.selectbox(
            label="**Region**",
            options=ss['region_list'],
            key="filter.region",
            format_func=lambda x: 'All' if x is None else x,
            on_change=process_region
        )

        st.sidebar.selectbox(
            label="**Subregion**",
            options=ss['subregion_list'],
            key="filter.subregion",
            format_func=lambda x: 'All' if x is None else x,
            on_change=process_subregion
        )

        st.sidebar.selectbox(
            label="**Country**",
            options=ss['country_list'],
            key="filter.country",
            format_func=lambda x: 'All' if x is None else x,
            on_change=process_country
        )

        st.sidebar.button(
            "Reset",
            type="primary",
            on_click=set_filters_to_default
        )

        st.sidebar.divider()


def process_region() -> None:
    """Update subregion and country options based on selected region."""
    ss = st.session_state
    rd = ss['region_data']
    region = ss['filter.region']
    subregion = ss['filter.subregion']
    country = ss['filter.country']

    if region:
        valid_data = rd[rd['region'] == region]
        if subregion not in valid_data['subregion'].values:
            ss['filter.subregion'] = None
        if country not in valid_data['country'].values:
            ss['filter.country'] = None
        ss['subregion_list'] = [None] + sorted(valid_data['subregion'].dropna().unique())
        ss['country_list'] = [None] + sorted(valid_data['country'].dropna().unique())
    else:
        ss['filter.subregion'] = None
        ss['filter.country'] = None
        ss['subregion_list'] = [None] + sorted(rd['subregion'].dropna().unique())
        ss['country_list'] = [None] + sorted(rd['country'].dropna().unique())

def process_subregion() -> None:
    """Update region and country options based on selected subregion."""
    ss = st.session_state
    rd = ss['region_data']
    region = ss['filter.region']
    subregion = ss['filter.subregion']
    country = ss['filter.country']

    if subregion:
        valid_data = rd[rd['subregion'] == subregion]
        if region not in valid_data['region'].values:
            ss['filter.region'] = valid_data.iloc[0]['region']
        if country not in valid_data['country'].values:
            ss['filter.country'] = None
        ss['country_list'] = [None] + sorted(valid_data['country'].dropna().unique())
    else:
        ss['filter.country'] = None
        if region:
            valid_data = rd[rd['region'] == region]
            ss['country_list'] = [None] + sorted(valid_data['country'].dropna().unique())
        else:
            ss['country_list'] = [None] + sorted(rd['country'].dropna().unique())

def process_country() -> None:
    """Update region and subregion based on selected country."""
    ss = st.session_state
    rd = ss['region_data']
    country = ss['filter.country']

    if country:
        valid_data = rd[rd['country'] == country]
        if not valid_data.empty:
            ss['filter.region'] = valid_data.iloc[0]['region']
            ss['filter.subregion'] = valid_data.iloc[0]['subregion']

def get_filtered_data() -> pd.DataFrame:
    """Return a filtered view of the data based on current filters."""
    ss = st.session_state

    # Get current filters
    start = ss["filter.start"]
    end = ss["filter.end"]
    classification_key = ss["filter.classification_key"].strip()
    region = ss["filter.region"]
    subregion = ss["filter.subregion"]
    country = ss["filter.country"]

    # Filter data
    data_filtered = ss['data'].copy()

    # Year filter
    data_filtered = data_filtered[
        (data_filtered['start_year'] >= start) & (data_filtered['end_year'] <= end)
    ]

    # Classification key filter (wildcard matching)
    if classification_key:
        data_filtered = data_filtered[
            data_filtered['classification_key'].str.contains(
                classification_key.replace('*', '.*'), regex=True, na=False
            )
        ]

    # Region/Subregion/Country filters
    if region:
        data_filtered = data_filtered[data_filtered['region'] == region]
    if subregion:
        data_filtered = data_filtered[data_filtered['subregion'] == subregion]
    if country:
        data_filtered = data_filtered[data_filtered['country'] == country]

    return data_filtered

def set_filters_to_default() -> None:
    """Reset filters to default full dataset."""
    ss = st.session_state
    data = ss["data"]
    rd = ss['region_data']

    ss['filter.disabled'] = False
    year_min = int(data['start_year'].min())
    year_max = int(data['start_year'].max())

    ss['filter.year_min'] = year_min
    ss['filter.year_max'] = year_max
    ss['filter.start'] = year_min
    ss['filter.end'] = year_max
    ss['filter.region'] = None
    ss['filter.subregion'] = None
    ss['filter.country'] = None

    ss['region_list'] = [None] + sorted(rd['region'].dropna().unique())
    ss['subregion_list'] = [None] + sorted(rd['subregion'].dropna().unique())
    ss['country_list'] = [None] + sorted(rd['country'].dropna().unique())
