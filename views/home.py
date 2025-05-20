import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.database import get_full_data
from utils.layout import PAGE_HELP_TEXT

# Set page
st.session_state['page'] = 'home'

# Load data only once into session state
if 'data' not in st.session_state:
    st.info("Connecting to the EM-DAT database...")
    data = get_full_data()
    st.session_state['data'] = data
    st.success("Data loaded successfully from database.")

    # Prepare region, subregion, country filters (correct Postgres fields)
    region_data = data[['region', 'subregion', 'country']].drop_duplicates()
    st.session_state['region_list'] = [None] + sorted(region_data['region'].dropna().unique())
    st.session_state['subregion_list'] = [None] + sorted(region_data['subregion'].dropna().unique())
    st.session_state['country_list'] = [None] + sorted(region_data['country'].dropna().unique())
    st.session_state['region_data'] = region_data

# Display page content
st.header('EM-VIEW Disaster Dashboard')
st.write(PAGE_HELP_TEXT[st.session_state['page']])

# Display database metadata
if "data" in st.session_state:
    data = st.session_state['data']
    
    st.subheader("Database Information")

    # Fix date fields for Postgres columns
    st.write(f"**Date range:** {int(data['start_year'].min())} - {int(data['end_year'].max())}")
    st.write(f"**Number of disaster records:** {len(data)}")

    # Show dataset preview
    with st.expander("Preview Dataset", expanded=False):
        st.dataframe(data.head(20), use_container_width=True)