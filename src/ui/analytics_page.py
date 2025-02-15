import streamlit as st
from src.data_manager import DataManager
from analytics.availability_analyzer import AvailabilityAnalyzer
from analytics.schedule_analyzer import ScheduleAnalyzer
from analytics.visualization import VisualizationManager

class AnalyticsPage:
    """Handles the analytics page UI and interactions."""
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize the analytics page.
        
        Args:
            data_manager (DataManager): Data manager instance
        """
        self.data_manager = data_manager
        self.visualization = VisualizationManager()
        
    def render(self):
        """Render the analytics page."""
        st.subheader("Analytics Dashboard")
        
        # Get availability data
        availability_data = self.data_manager.get_availability_data()
        if availability_data is not None:
            # Initialize analyzers
            availability_analyzer = AvailabilityAnalyzer(availability_data)
            
            # Availability Overview
            st.subheader("Overall Availability")
            availability_summary = availability_analyzer.get_availability_summary()
            chart = self.visualization.create_availability_chart(
                availability_summary,
                availability_analyzer.sorted_dates.strftime("%d/%m").tolist()
            )
            st.altair_chart(chart, use_container_width=True)
            
            # Member Availability Stats
            st.subheader("Member Availability")
            member_stats = availability_analyzer.get_member_availability_stats()
            member_chart = self.visualization.create_member_availability_chart(member_stats)
            st.altair_chart(member_chart, use_container_width=True)
            
            # Schedule Analysis
            st.subheader("Schedule Analysis")
            final_schedule = self.data_manager.get_final_schedule()
            if final_schedule is not None:
                schedule_analyzer = ScheduleAnalyzer(final_schedule)
                
                # Assignment Distribution
                assignments = schedule_analyzer.get_assignment_distribution()
                assignment_chart = self.visualization.create_assignment_distribution_chart(
                    assignments
                )
                st.altair_chart(assignment_chart, use_container_width=True)
                
                # Role Distribution
                role_dist = schedule_analyzer.get_role_distribution()
                role_chart = self.visualization.create_role_distribution_chart(role_dist)
                st.altair_chart(role_chart, use_container_width=True)
                
                # Fairness Metrics
                st.subheader("Fairness Analysis")
                metrics = schedule_analyzer.calculate_fairness_metrics()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fairness Score", f"{metrics['fairness_score']:.1f}%")
                with col2:
                    st.metric("Max Deviation", f"{metrics['max_deviation']:.1f}")
                with col3:
                    st.metric("Gini Coefficient", f"{metrics['gini_coefficient']:.3f}")
                
                # Role Diversity
                diversity = schedule_analyzer.get_member_role_diversity()
                diversity_chart = self.visualization.create_role_diversity_chart(diversity)
                st.altair_chart(diversity_chart, use_container_width=True)
            else:
                st.info("No final schedule data available for analysis.")
        else:
            st.error("No availability data loaded.")