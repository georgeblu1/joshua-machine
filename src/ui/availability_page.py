import streamlit as st
import pandas as pd
from src.data_manager import DataManager
from availability.availability_checker import AvailabilityChecker
from availability.role_matcher import RoleMatcher

class AvailabilityPage:
    """Handles the availability checking page UI and interactions."""
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize the availability page.
        
        Args:
            data_manager (DataManager): Data manager instance
        """
        self.data_manager = data_manager
        
    def render(self):
        """Render the availability checking page."""
        st.subheader("Check Availability")
        
        # Get availability and role data
        availability_data = self.data_manager.get_availability_data()
        if availability_data is not None:
            role_data = self.data_manager.get_role_data(["vocal_main", "vocal_sub", 
                                                        "piano", "drum", "bass", 
                                                        "pa", "ppt"])
            
            # Initialize checkers
            availability_checker = AvailabilityChecker(availability_data, role_data)
            role_matcher = RoleMatcher(role_data)
            
            # Date selection
            available_dates = availability_checker.get_available_dates()
            selected_date = st.selectbox(
                "Select a Date to Check Availability",
                available_dates
            )
            
            if selected_date:
                # Get available people
                available_people = availability_checker.get_available_people_for_date(
                    selected_date
                )
                
                if available_people:
                    # Show role availability
                    st.subheader("Role Availability")
                    role_availability = availability_checker.get_role_availability(
                        selected_date
                    )
                    
                    # Create and display availability table
                    availability_df = pd.DataFrame.from_dict(
                        {role: ", ".join(people) if people else "None"
                         for role, people in role_availability.items()},
                        orient="index",
                        columns=["Available People"]
                    )
                    availability_df.index.name = "Role"
                    st.table(availability_df)
                    
                    # Show coverage issues
                    issues = availability_checker.get_coverage_issues(selected_date)
                    if issues:
                        st.warning("Coverage Issues Detected:")
                        for role, issue in issues.items():
                            st.write(f"- {role}: {issue}")
                            
                    # Show role coverage
                    st.subheader("Role Coverage")
                    coverage = role_matcher.get_role_coverage(available_people)
                    coverage_df = pd.DataFrame.from_dict(
                        coverage,
                        orient="index",
                        columns=["Coverage (%)"]
                    )
                    coverage_df.index.name = "Role"
                    st.table(coverage_df)
                else:
                    st.warning(f"No one is available on {selected_date}.")
        else:
            st.info("Please load availability data first.")