from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime

class AvailabilityAnalyzer:
    """Analyzes member availability patterns and trends."""
    
    def __init__(self, availability_data: pd.DataFrame):
        """
        Initialize the analyzer with availability data.
        
        Args:
            availability_data (pd.DataFrame): Raw availability data
        """
        self.data = availability_data
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare and clean the availability data for analysis."""
        if self.data is None:
            return
            
        self.date_columns = self.data.columns[1:]  # Exclude name column
        
        # Append current year for proper date parsing
        current_year = datetime.now().year
        self.formatted_dates = f"{current_year}/" + self.date_columns
        
        # Convert to datetime and sort
        self.sorted_dates = pd.to_datetime(
            self.formatted_dates, 
            format="%Y/%d/%m", 
            errors="coerce"
        ).sort_values()
        
        # Update column order
        self.sorted_column_names = ["Name List"] + self.sorted_dates.strftime("%d/%m").tolist()
        self.data = self.data[self.sorted_column_names]
        
    def get_availability_summary(self) -> pd.DataFrame:
        """
        Get summary of availability counts per date.
        
        Returns:
            pd.DataFrame: Summary of availability
        """
        if self.data is None:
            return pd.DataFrame()
            
        summary = self.data.iloc[:, 1:].apply(
            lambda x: (x == 'Yes').sum()
        ).reset_index()
        
        summary.columns = ["Date", "Count"]
        
        # Add datetime for sorting
        current_year = datetime.now().year
        summary["Date_dt"] = pd.to_datetime(
            f"{current_year}/" + summary["Date"],
            format="%Y/%d/%m"
        )
        
        return summary
        
    def get_member_availability_stats(self) -> pd.DataFrame:
        """
        Get detailed availability statistics for each member.
        
        Returns:
            pd.DataFrame: Member availability statistics
        """
        if self.data is None:
            return pd.DataFrame()
            
        melted_df = self.data.melt(
            id_vars=["Name List"],
            var_name="Date",
            value_name="Availability"
        )
        
        # Group by name and availability status
        grouped = melted_df.groupby(
            ["Name List", "Availability"]
        ).size().unstack(fill_value=0)
        
        # Calculate additional statistics
        grouped['Total_Days'] = grouped['Yes'] + grouped['No']
        grouped['Availability_Rate'] = (grouped['Yes'] / grouped['Total_Days'] * 100).round(2)
        
        return grouped.sort_values(by='Availability_Rate', ascending=False)
        
    def get_date_difficulty_scores(self) -> pd.DataFrame:
        """
        Calculate difficulty scores for each date based on availability.
        
        Returns:
            pd.DataFrame: Date difficulty scores
        """
        if self.data is None:
            return pd.DataFrame()
            
        summary = self.get_availability_summary()
        total_members = len(self.data)
        
        summary['Difficulty_Score'] = (
            (total_members - summary['Count']) / total_members * 100
        ).round(2)
        
        return summary.sort_values('Difficulty_Score', ascending=False)
        
    def get_weekly_patterns(self) -> Dict[str, float]:
        """
        Analyze availability patterns by day of week.
        
        Returns:
            Dict[str, float]: Average availability rate by day of week
        """
        if self.data is None:
            return {}
            
        summary = self.get_availability_summary()
        summary['DayOfWeek'] = summary['Date_dt'].dt.day_name()
        
        weekly_patterns = summary.groupby('DayOfWeek')['Count'].mean().round(2)
        return weekly_patterns.to_dict()
        
    def get_availability_trends(self, window: int = 3) -> pd.DataFrame:
        """
        Calculate availability trends over time.
        
        Args:
            window (int): Rolling window size for trend calculation
            
        Returns:
            pd.DataFrame: Availability trends
        """
        if self.data is None:
            return pd.DataFrame()
            
        summary = self.get_availability_summary()
        summary['Rolling_Avg'] = summary['Count'].rolling(window=window).mean()
        summary['Trend'] = summary['Rolling_Avg'].diff()
        
        return summary