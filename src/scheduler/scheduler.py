from typing import Dict, List, Optional
import pandas as pd
import streamlit as st
from .role_manager import RoleManager

class Scheduler:
    """Handles the core scheduling logic."""
    
    def __init__(self, role_manager: RoleManager):
        """
        Initialize Scheduler with a RoleManager.
        
        Args:
            role_manager (RoleManager): The role manager to use for assignments
        """
        self.role_manager = role_manager
        
    def _assign_roles_for_date(self,
                              available_people: List[str],
                              date: str,
                              scheduled: Optional[pd.DataFrame] = None) -> Dict[str, Optional[str]]:
        """
        Assign roles for a specific date.
        
        Args:
            available_people (List[str]): List of available people
            date (str): The date to schedule
            scheduled (Optional[pd.DataFrame]): Previously scheduled dates
            
        Returns:
            Dict[str, Optional[str]]: Dictionary mapping roles to assigned people
        """
        assignments = {role: None for role in RoleManager.ROLES}
        assigned_people = set()
        
        # Priority order for role assignment
        priority_roles = [
            ('vocal_main', 'vocal_main'),
            ('vocal_sub1', 'vocal_sub'),
            ('vocal_sub2', 'vocal_sub'),
            ('piano', 'piano'),
            ('drum', 'drum'),
            ('bass', 'bass'),
            ('pa', 'pa'),
            ('ppt', 'ppt')
        ]
        
        for role, sheet_name in priority_roles:
            # Get people who are still available
            remaining_people = [p for p in available_people if p not in assigned_people]
            
            if not remaining_people:
                continue
                
            # Get qualified people for this role
            qualified_people = self.role_manager.get_qualified_people(role, remaining_people)
            
            if not qualified_people:
                continue
                
            if role == 'vocal_main':
                selected = self.role_manager.select_person(qualified_people, role, scheduled)
                
            elif role in ['vocal_sub1', 'vocal_sub2']:
                # For vocal_sub2, exclude person assigned to vocal_sub1
                excluded = {assignments['vocal_sub1']} if role == 'vocal_sub2' and assignments['vocal_sub1'] else set()
                selected = self.role_manager.select_person(qualified_people, role, scheduled, excluded)
                
            else:  # Other roles
                selected = self.role_manager.select_person(qualified_people, role, scheduled)
                
            if selected:
                assignments[role] = selected
                assigned_people.add(selected)
                
        return assignments
        
    def generate_schedule(self, availability_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Generate a complete schedule based on availability data.
        
        Args:
            availability_data (pd.DataFrame): The availability data
            
        Returns:
            Optional[pd.DataFrame]: The generated schedule
        """
        if availability_data is None:
            st.error("No availability data provided")
            return None
            
        date_columns = availability_data.columns[1:]  # Skip the first column (names)
        scheduled = pd.DataFrame(index=RoleManager.ROLES, columns=date_columns)
        
        # Generate schedule sequentially
        for date in date_columns:
            available_people = availability_data[
                availability_data[date] == 'Yes'
            ].iloc[:, 0].tolist()
            
            assignments = self._assign_roles_for_date(available_people, date, scheduled)
            
            # Update schedule
            for role, person in assignments.items():
                scheduled.at[role, date] = person
                
        return scheduled