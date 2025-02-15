import streamlit as st
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.data_manager import DataManager
from src.ui.scheduling_page import SchedulingPage
from src.ui.analytics_page import AnalyticsPage
from src.ui.availability_page import AvailabilityPage

def initialize_session_state():
    """Initialize session state variables."""
    if 'sheet_key' not in st.session_state:
        st.session_state.sheet_key = None
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = None
    if 'generated_schedule' not in st.session_state:
        st.session_state.generated_schedule = None

def main():
    """Main application entry point."""
    st.title("Joshua Machine")
    st.subheader("Connaught Church Service Scheduler")
    
    # Initialize session state
    initialize_session_state()
    
    # Google Sheet Connection
    if st.session_state.sheet_key is None:
        st.subheader("Google Sheet Connection")
        credentials_path = "credentials.json"
        sheet_key = st.text_input("Enter Google Sheet Key")
        
        if st.button("Connect to Google Sheet"):
            data_manager = DataManager(credentials_path)
            if data_manager.connect_to_sheet(sheet_key):
                st.session_state.sheet_key = sheet_key
                st.session_state.data_manager = data_manager
                st.success("Successfully connected to Google Sheet!")
            else:
                st.error("Failed to connect to the Google Sheet.")
    else:
        st.success(f"Connected to Google Sheet: {st.session_state.sheet_key}")
    
    # Navigation
    if st.session_state.data_manager is not None:
        st.sidebar.header("Navigation")
        selected_tab = st.sidebar.radio(
            "Choose a tab:",
            ["Scheduling", "Analytics", "Check Availability"]
        )
        
        # Initialize page objects
        scheduling_page = SchedulingPage(st.session_state.data_manager)
        analytics_page = AnalyticsPage(st.session_state.data_manager)
        availability_page = AvailabilityPage(st.session_state.data_manager)
        
        # Render selected page
        if selected_tab == "Scheduling":
            scheduling_page.render()
        elif selected_tab == "Analytics":
            analytics_page.render()
        else:  # Check Availability
            availability_page.render()

if __name__ == "__main__":
    main()