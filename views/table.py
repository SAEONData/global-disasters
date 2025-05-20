import streamlit as st

from utils.filters import get_filtered_data
from utils.layout import PAGE_HELP_TEXT

# Default columns for table view - use Postgres field names
DEFAULT_COLUMNS = [
    "disno",
    "country",
    "disaster_type",
    "total_deaths",
    "total_affected",
    "total_damage_adjusted_usd_thousands"
]

# Format numbers for start and end years
DEFAULT_STYLE = {
    "start_year": '{:.0f}',
    "end_year": '{:.0f}'
}

# Set page
st.session_state["page"] = "table"

# Check if data is loaded
if "data" not in st.session_state:
    st.error('No disaster data available. Please check database connection.', icon="🚨")
else:
    data = get_filtered_data()

    columns = st.multiselect(
        "Select columns:",
        data.columns,
        default=DEFAULT_COLUMNS
    )

    display_rows = 15

    st.dataframe(
        data[columns].style.format(
            DEFAULT_STYLE,
            precision=0,
            thousands=','
        ),
        height=(display_rows + 1) * 35 + 3,
        use_container_width=True
    )

    # Page Help
    with st.expander("See page details", expanded=False, icon=':material/info:'):
        st.markdown(PAGE_HELP_TEXT[st.session_state.page])
