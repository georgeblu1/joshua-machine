from typing import Dict, List, Optional
import pandas as pd

class ScheduleAnalyzer:
    """Analyzes schedule patterns and fairness metrics."""
    
    def __init__(self, schedule_data: pd.DataFrame):
        """
        Initialize the analyzer with schedule data.
        
        Args:
            schedule_data (pd.DataFrame): Final schedule data
        """
        self.data = schedule_data
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare schedule data for analysis."""
        if self.data is None:
            return
            
        # Reshape data to long format
        self.melted_data = self.data.melt(
            id_vars=["role"],
            var_name="Date",
            value_name="Person"
        ).dropna()
        
        # Ensure uniform data types
        self.melted_data["Person"] = self.melted_data["Person"].fillna("Unassigned")
        
    def get_assignment_distribution(self) -> pd.DataFrame:
        """
        Get distribution of assignments per person.
        
        Returns:
            pd.DataFrame: Assignment counts and statistics
        """
        if self.data is None:
            return pd.DataFrame()
            
        assignments = self.melted_data.groupby("Person").size().reset_index(name="Count")
        
        # Calculate statistics
        total_assignments = assignments["Count"].sum()
        assignments["Percentage"] = (assignments["Count"] / total_assignments * 100).round(2)
        assignments["Expected"] = total_assignments / len(assignments)
        assignments["Deviation"] = assignments["Count"] - assignments["Expected"]
        
        return assignments.sort_values("Count", ascending=False)
        
    def get_role_distribution(self) -> pd.DataFrame:
        """
        Get distribution of assignments per role.
        
        Returns:
            pd.DataFrame: Role assignment statistics
        """
        if self.data is None:
            return pd.DataFrame()
            
        role_counts = self.melted_data.groupby("role").size().reset_index(name="Count")
        return role_counts.sort_values("Count", ascending=False)
        
    def calculate_fairness_metrics(self) -> Dict[str, float]:
        """
        Calculate various fairness metrics for the schedule.
        
        Returns:
            Dict[str, float]: Dictionary of fairness metrics
        """
        if self.data is None:
            return {}
            
        assignments = self.get_assignment_distribution()
        
        metrics = {
            "gini_coefficient": self._calculate_gini(assignments["Count"]),
            "std_deviation": assignments["Count"].std(),
            "max_deviation": abs(assignments["Deviation"]).max(),
            "fairness_score": self._calculate_fairness_score(assignments)
        }
        
        return metrics
        
    def _calculate_gini(self, values: pd.Series) -> float:
        """
        Calculate Gini coefficient for assignment distribution.
        
        Args:
            values (pd.Series): Series of values to calculate Gini coefficient for
            
        Returns:
            float: Gini coefficient
        """
        sorted_values = values.sort_values()
        n = len(sorted_values)
        index = range(1, n + 1)
        return ((2 * sum(i * val for i, val in zip(index, sorted_values))) / 
                (n * sum(sorted_values)) - (n + 1) / n)
        
    def _calculate_fairness_score(self, assignments: pd.DataFrame) -> float:
        """
        Calculate overall fairness score (0-100).
        
        Args:
            assignments (pd.DataFrame): Assignment distribution data
            
        Returns:
            float: Fairness score
        """
        max_deviation = abs(assignments["Deviation"]).max()
        expected = assignments["Expected"].iloc[0]
        
        # Score from 0-100 where 100 is perfectly fair
        score = 100 * (1 - (max_deviation / expected))
        return max(0, min(100, score))
        
    def get_member_role_diversity(self) -> pd.DataFrame:
        """
        Calculate role diversity for each member.
        
        Returns:
            pd.DataFrame: Role diversity statistics
        """
        if self.data is None:
            return pd.DataFrame()
            
        # Count unique roles per person
        diversity = self.melted_data.groupby("Person").agg({
            "role": ["count", "nunique"]
        }).reset_index()
        
        diversity.columns = ["Person", "Total_Assignments", "Unique_Roles"]
        diversity["Role_Diversity"] = (
            diversity["Unique_Roles"] / diversity["Total_Assignments"] * 100
        ).round(2)
        
        return diversity.sort_values("Role_Diversity", ascending=False)
        
    def get_role_succession_patterns(self) -> pd.DataFrame:
        """
        Analyze patterns in role assignments over consecutive dates.
        
        Returns:
            pd.DataFrame: Succession patterns
        """
        if self.data is None:
            return pd.DataFrame()
            
        # Sort by date and analyze transitions
        sorted_data = self.melted_data.sort_values("Date")
        transitions = pd.DataFrame({
            'role': sorted_data['role'],
            'current_person': sorted_data['Person'],
            'next_person': sorted_data['Person'].shift(-1)
        }).dropna()
        
        return transitions.groupby(['role', 'current_person', 'next_person']).size()