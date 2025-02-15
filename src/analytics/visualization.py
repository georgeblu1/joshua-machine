from typing import Dict, List, Optional
import altair as alt
import pandas as pd

class VisualizationManager:
    """Manages creation of all visualization charts."""
    
    @staticmethod
    def create_availability_chart(summary_data: pd.DataFrame, 
                                sorted_dates: List[str]) -> alt.Chart:
        """
        Create availability overview chart.
        
        Args:
            summary_data (pd.DataFrame): Availability summary data
            sorted_dates (List[str]): List of sorted dates
            
        Returns:
            alt.Chart: Altair chart object
        """
        return alt.Chart(summary_data).mark_bar().encode(
            x=alt.X("Date:N", title="Date", sort=sorted_dates),
            y=alt.Y("Count:Q", title="Number of Available People"),
            tooltip=["Date", "Count"]
        ).properties(
            width=1500,
            height=400,
            title="Availability Overview (Individual Dates)"
        )
        
    @staticmethod
    def create_member_availability_chart(member_data: pd.DataFrame) -> alt.Chart:
        """
        Create member availability distribution chart.
        
        Args:
            member_data (pd.DataFrame): Member availability data
            
        Returns:
            alt.Chart: Altair chart object
        """
        chart_data = member_data.reset_index()
        melted_data = chart_data.melt(
            id_vars="Name List",
            value_vars=["Yes", "No"],
            var_name="Availability",
            value_name="Count"
        )
        
        return alt.Chart(melted_data).mark_bar().encode(
            x=alt.X("Count:Q", stack="normalize", title="Percentage"),
            y=alt.Y("Name List:N", sort="-x", title="Person"),
            color=alt.Color(
                "Availability:N",
                scale=alt.Scale(domain=["Yes", "No"], range=["#1f77b4", "#d62728"])
            ),
            tooltip=["Name List", "Availability", "Count"]
        ).properties(
            width=1500,
            height=max(30 * len(member_data), 500),
            title="Availability Distribution per Person"
        )
        
    @staticmethod
    def create_assignment_distribution_chart(
        assignment_data: pd.DataFrame
    ) -> alt.Chart:
        """
        Create assignment distribution chart.
        
        Args:
            assignment_data (pd.DataFrame): Assignment distribution data
            
        Returns:
            alt.Chart: Altair chart object
        """
        return alt.Chart(assignment_data).mark_bar().encode(
            x=alt.X("Person:N", sort="-y", title="Person"),
            y=alt.Y("Count:Q", title="Number of Assignments"),
            tooltip=["Person", "Count", "Percentage"]
        ).properties(
            width=800,
            height=400,
            title="Assignments per Person"
        )
        
    @staticmethod
    def create_role_distribution_chart(role_data: pd.DataFrame) -> alt.Chart:
        """
        Create role distribution chart.
        
        Args:
            role_data (pd.DataFrame): Role distribution data
            
        Returns:
            alt.Chart: Altair chart object
        """
        return alt.Chart(role_data).mark_bar().encode(
            x=alt.X("role:N", sort="-y", title="Role"),
            y=alt.Y("Count:Q", title="Number of Assignments"),
            tooltip=["role", "Count"]
        ).properties(
            width=800,
            height=400,
            title="Assignments per Role"
        )
        
    @staticmethod
    def create_fairness_deviation_chart(
        assignment_data: pd.DataFrame
    ) -> alt.Chart:
        """
        Create fairness deviation chart.
        
        Args:
            assignment_data (pd.DataFrame): Assignment data with deviations
            
        Returns:
            alt.Chart: Altair chart object
        """
        return alt.Chart(assignment_data).mark_bar().encode(
            x=alt.X("Person:N", sort="-y", title="Person"),
            y=alt.Y("Deviation:Q", title="Deviation from Average"),
            color=alt.condition(
                alt.datum.Deviation > 0,
                alt.value("#1f77b4"),  # Blue for above average
                alt.value("#d62728")   # Red for below average
            ),
            tooltip=["Person", "Count", "Deviation"]
        ).properties(
            width=800,
            height=400,
            title="Deviation from Average Assignments"
        )
    
    @staticmethod
    def create_role_diversity_chart(diversity_data: pd.DataFrame) -> alt.Chart:
        """
        Create role diversity chart.
        
        Args:
            diversity_data (pd.DataFrame): Role diversity data
            
        Returns:
            alt.Chart: Altair chart object
        """
        return alt.Chart(diversity_data).mark_bar().encode(
            x=alt.X("Person:N", sort="-y", title="Person"),
            y=alt.Y("Role_Diversity:Q", title="Role Diversity (%)"),
            tooltip=["Person", "Total_Assignments", "Unique_Roles", "Role_Diversity"]
        ).properties(
            width=800,
            height=400,
            title="Role Diversity per Person"
        )
    
    @staticmethod
    def create_weekly_patterns_chart(patterns_data: pd.DataFrame) -> alt.Chart:
        """
        Create weekly patterns chart.
        
        Args:
            patterns_data (pd.DataFrame): Weekly patterns data
            
        Returns:
            alt.Chart: Altair chart object
        """
        # Convert dictionary to DataFrame if needed
        if isinstance(patterns_data, dict):
            patterns_data = pd.DataFrame(
                list(patterns_data.items()),
                columns=['DayOfWeek', 'Average']
            )
        
        return alt.Chart(patterns_data).mark_bar().encode(
            x=alt.X("DayOfWeek:N", title="Day of Week",
                   sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']),
            y=alt.Y("Average:Q", title="Average Availability"),
            tooltip=["DayOfWeek", "Average"]
        ).properties(
            width=800,
            height=400,
            title="Average Availability by Day of Week"
        )