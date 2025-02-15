import streamlit as st
import sys
from pathlib import Path
from io import BytesIO

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from src.data_manager import DataManager, DataSource
from src.ui.scheduling_page import SchedulingPage
from src.ui.analytics_page import AnalyticsPage
from src.ui.availability_page import AvailabilityPage

def initialize_session_state():
    """Initialize session state variables."""
    if 'data_source' not in st.session_state:
        st.session_state.data_source = None
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = None
    if 'generated_schedule' not in st.session_state:
        st.session_state.generated_schedule = None

def handle_excel_upload():
    """Handle Excel file upload."""
    uploaded_file = st.file_uploader("Upload Schedule Excel File", type=['xlsx'])
    if uploaded_file is not None:
        try:
            data_manager = DataManager()
            if data_manager.connect_to_source(
                DataSource.EXCEL,
                file_data=BytesIO(uploaded_file.getvalue())
            ):
                st.session_state.data_source = DataSource.EXCEL
                st.session_state.data_manager = data_manager
                st.success("Successfully loaded Excel file!")
                return True
        except Exception as e:
            st.error(f"Error loading Excel file: {str(e)}")
    return False

def handle_google_sheets():
    """Handle Google Sheets connection."""
    credentials_path = "credentials.json"
    sheet_key = st.text_input("Enter Google Sheet Key")
    
    if st.button("Connect to Google Sheet"):
        try:
            data_manager = DataManager()
            data_manager.initialize_google_sheets(credentials_path)
            if data_manager.connect_to_source(
                DataSource.GOOGLE_SHEETS,
                sheet_key=sheet_key
            ):
                st.session_state.data_source = DataSource.GOOGLE_SHEETS
                st.session_state.data_manager = data_manager
                st.success("Successfully connected to Google Sheet!")
                return True
        except Exception as e:
            st.error(f"Error connecting to Google Sheet: {str(e)}")
    return False

def main():
    """Main application entry point."""
    st.title("Joshua Machine")
    st.subheader("Church Service Scheduler")
    
    # Initialize session state
    initialize_session_state()
    
    # Data Source Selection
    if st.session_state.data_manager is None:
        st.subheader("Select Data Source")
        source_type = st.radio(
            "Choose your data source:",
            ["Upload Excel File", "Connect to Google Sheets"]
        )
        
        if source_type == "Upload Excel File":
            if handle_excel_upload():
                st.rerun()
        else:
            if handle_google_sheets():
                st.rerun()
    else:
        # Show current connection status
        source_type = "Excel file" if st.session_state.data_source == DataSource.EXCEL else "Google Sheet"
        st.success(f"Connected to {source_type}")
        
        # Add option to change data source
        if st.button("Change Data Source"):
            st.session_state.data_manager = None
            st.session_state.data_source = None
            st.session_state.generated_schedule = None
            st.rerun()
    
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