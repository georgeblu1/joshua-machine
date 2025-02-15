import streamlit as st
from typing import Optional
import pandas as pd
from src.data_manager import DataManager
from src.scheduler.scheduler import Scheduler
from src.scheduler.role_manager import RoleManager

class SchedulingPage:
    """Handles the scheduling page UI and interactions."""
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize the scheduling page.
        
        Args:
            data_manager (DataManager): Data manager instance
        """
        self.data_manager = data_manager
        
    def render(self):
        """Render the scheduling page."""
        st.subheader("Schedule Generation")
        
        # Display current availability data
        availability_data = self.data_manager.get_availability_data()
        if availability_data is not None:
            st.subheader("Current Availability Data")
            st.dataframe(availability_data)
            
            # Load role data
            role_data = self.data_manager.get_role_data(["vocal_main", "vocal_sub", 
                                                        "piano", "drum", "bass", 
                                                        "pa", "ppt"])
            
            if role_data:
                # Initialize role manager and scheduler
                role_manager = RoleManager(role_data)
                scheduler = Scheduler(role_manager)
                
                # Generate schedule button
                if st.button("Generate Schedule", key="generate_button"):
                    with st.spinner("Generating schedule..."):
                        schedule = scheduler.generate_schedule(availability_data)
                        if schedule is not None:
                            st.session_state.generated_schedule = schedule
                            st.success("Schedule generated successfully!")
                        else:
                            st.error("Failed to generate schedule!")
                
                # Display and save generated schedule
                if 'generated_schedule' in st.session_state:
                    st.subheader("Generated Schedule")
                    st.dataframe(st.session_state.generated_schedule)
                    
                    # Password protection for saving
                    password = st.text_input(
                        "Enter password to save the schedule:",
                        type="password",
                        key="save_password"
                    )
                    
                    if password == "123456":  # In production, use environment variables
                        st.success("Password accepted. You can now save the schedule.")
                        if st.button("Save Schedule to Google Sheet", key="save_button"):
                            if self.data_manager.save_final_schedule(
                                st.session_state.generated_schedule
                            ):
                                st.success("Schedule successfully saved to Google Sheet!")
                    elif password != "":
                        st.error("Incorrect password. Please try again.")
        else:
            st.info("Please load availability data first.")