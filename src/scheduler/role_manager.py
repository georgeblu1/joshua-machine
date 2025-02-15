from typing import Dict, List, Set, Optional
import pandas as pd
import random

class RoleManager:
    """Manages role assignments and constraints."""
    
    ROLES = [
        'vocal_main',
        'vocal_sub1',
        'vocal_sub2',
        'piano',
        'drum',
        'bass',
        'pa',
        'ppt'
    ]
    
    ROLE_SHEETS = {
        'vocal_main': 'vocal_main',
        'vocal_sub1': 'vocal_sub',
        'vocal_sub2': 'vocal_sub',
        'piano': 'piano',
        'drum': 'drum',
        'bass': 'bass',
        'pa': 'pa',
        'ppt': 'ppt'
    }
    
    def __init__(self, role_data: Dict[str, pd.DataFrame]):
        """
        Initialize RoleManager with role qualification data.
        
        Args:
            role_data (Dict[str, pd.DataFrame]): Dictionary mapping role titles to qualification data
        """
        self.role_data = role_data
        
    def get_qualified_people(self, role: str, available_people: List[str]) -> List[str]:
        """
        Get list of people qualified for a specific role from available people.
        
        Args:
            role (str): The role to check qualifications for
            available_people (List[str]): List of available people
            
        Returns:
            List[str]: List of qualified people
        """
        sheet_name = self.ROLE_SHEETS[role]
        if sheet_name not in self.role_data:
            return []
            
        qualified = self.role_data[sheet_name]['name'].values
        return [p for p in available_people if p in qualified]
        
    def get_assignment_counts(self, role: str, people: List[str], past_schedule: Optional[pd.DataFrame]) -> Dict[str, int]:
        """
        Calculate how many times each person has been assigned to a role.
        
        Args:
            role (str): The role to check
            people (List[str]): List of people to check
            past_schedule (Optional[pd.DataFrame]): Previous schedule data
            
        Returns:
            Dict[str, int]: Dictionary mapping people to their assignment counts
        """
        if past_schedule is None or past_schedule.empty:
            return {person: 0 for person in people}
            
        counts = {}
        for person in people:
            count = (past_schedule.loc[role] == person).sum()
            counts[person] = count
        return counts
        
    def select_person(self, 
                     available_candidates: List[str],
                     role: str,
                     past_schedule: Optional[pd.DataFrame],
                     excluded_people: Set[str] = None) -> Optional[str]:
        """
        Select a person for a role based on past assignments and constraints.
        
        Args:
            available_candidates (List[str]): List of available candidates
            role (str): The role to fill
            past_schedule (Optional[pd.DataFrame]): Previous schedule data
            excluded_people (Set[str]): People to exclude from selection
            
        Returns:
            Optional[str]: Selected person or None if no one is available
        """
        if not available_candidates:
            return None
            
        if excluded_people:
            available_candidates = [p for p in available_candidates if p not in excluded_people]
            
        if not available_candidates:
            return None
            
        # Get historical assignment counts
        assignment_counts = self.get_assignment_counts(role, available_candidates, past_schedule)
        
        # Find the minimum number of assignments
        min_assignments = min(assignment_counts.values())
        
        # Get all people with the minimum number of assignments
        candidates = [p for p, count in assignment_counts.items() if count == min_assignments]
        
        # Randomly select from the candidates
        return random.choice(candidates)