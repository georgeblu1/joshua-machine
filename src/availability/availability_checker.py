from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

class AvailabilityChecker:
    """Handles checking availability for specific dates and roles."""
    
    def __init__(self, availability_data: pd.DataFrame, role_data: Dict[str, pd.DataFrame]):
        """
        Initialize the availability checker.
        
        Args:
            availability_data (pd.DataFrame): Member availability data
            role_data (Dict[str, pd.DataFrame]): Role qualification data
        """
        self.availability_data = availability_data
        self.role_data = role_data
        
    def get_available_dates(self) -> List[str]:
        """
        Get list of all available dates.
        
        Returns:
            List[str]: List of dates
        """
        if self.availability_data is None:
            return []
        return list(self.availability_data.columns[1:])  # Exclude name column
        
    def get_available_people_for_date(self, date: str) -> List[str]:
        """
        Get list of available people for a specific date.
        
        Args:
            date (str): The date to check
            
        Returns:
            List[str]: List of available people
        """
        if self.availability_data is None or date not in self.availability_data.columns:
            return []
            
        return self.availability_data[
            self.availability_data[date] == "Yes"
        ]["Name List"].tolist()
        
    def get_qualified_people_for_role(self, role: str) -> List[str]:
        """
        Get list of people qualified for a specific role.
        
        Args:
            role (str): The role to check
            
        Returns:
            List[str]: List of qualified people
        """
        if role not in self.role_data:
            return []
            
        return self.role_data[role]["name"].values.tolist()
        
    def get_role_availability(self, date: str) -> Dict[str, List[str]]:
        """
        Get available people for each role on a specific date.
        
        Args:
            date (str): The date to check
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping roles to available people
        """
        available_people = self.get_available_people_for_date(date)
        role_availability = {}
        
        for role, data in self.role_data.items():
            qualified_people = self.get_qualified_people_for_role(role)
            available_for_role = list(set(available_people) & set(qualified_people))
            role_availability[role] = available_for_role
            
        return role_availability
        
    def get_coverage_issues(self, date: str) -> Dict[str, str]:
        """
        Check for potential coverage issues on a specific date.
        
        Args:
            date (str): The date to check
            
        Returns:
            Dict[str, str]: Dictionary of roles with coverage issues
        """
        role_availability = self.get_role_availability(date)
        issues = {}
        
        for role, available_people in role_availability.items():
            if not available_people:
                issues[role] = "No one available"
            elif len(available_people) < 2:  # Could be configured per role
                issues[role] = "Limited availability"
                
        return issues
        
    def get_member_availability_calendar(self, member: str) -> Dict[str, str]:
        """
        Get availability calendar for a specific member.
        
        Args:
            member (str): The member to check
            
        Returns:
            Dict[str, str]: Dictionary mapping dates to availability
        """
        if self.availability_data is None or member not in self.availability_data["Name List"].values:
            return {}
            
        member_data = self.availability_data[
            self.availability_data["Name List"] == member
        ].iloc[0]
        
        return member_data[1:].to_dict()  # Exclude name column
        
    def get_role_coverage_calendar(self) -> Dict[str, Dict[str, int]]:
        """
        Get calendar showing number of available people per role per date.
        
        Returns:
            Dict[str, Dict[str, int]]: Nested dictionary of role coverage
        """
        dates = self.get_available_dates()
        coverage_calendar = {}
        
        for date in dates:
            role_availability = self.get_role_availability(date)
            coverage_calendar[date] = {
                role: len(people) for role, people in role_availability.items()
            }
            
        return coverage_calendar