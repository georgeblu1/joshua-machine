from typing import Dict, List, Set, Optional
import pandas as pd

class RoleMatcher:
    """Handles matching available people to roles based on qualifications."""
    
    def __init__(self, role_data: Dict[str, pd.DataFrame]):
        """
        Initialize the role matcher.
        
        Args:
            role_data (Dict[str, pd.DataFrame]): Role qualification data
        """
        self.role_data = role_data
        self.role_requirements = self._initialize_role_requirements()
        
    def _initialize_role_requirements(self) -> Dict[str, Dict]:
        """
        Initialize role requirements and constraints.
        
        Returns:
            Dict[str, Dict]: Dictionary of role requirements
        """
        return {
            'vocal_main': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            },
            'vocal_sub': {
                'min_people': 2,
                'max_people': 2,
                'conflicts': ['vocal_main']
            },
            'piano': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            },
            'drum': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            },
            'bass': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            },
            'pa': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            },
            'ppt': {
                'min_people': 1,
                'max_people': 1,
                'conflicts': []
            }
        }
        
    def get_role_requirements(self, role: str) -> Dict:
        """
        Get requirements for a specific role.
        
        Args:
            role (str): The role to check
            
        Returns:
            Dict: Role requirements
        """
        return self.role_requirements.get(role, {})
        
    def get_qualified_people(self, role: str, available_people: List[str]) -> List[str]:
        """
        Get list of qualified people for a role from available people.
        
        Args:
            role (str): The role to check
            available_people (List[str]): List of available people
            
        Returns:
            List[str]: List of qualified people
        """
        if role not in self.role_data:
            return []
            
        qualified = self.role_data[role]['name'].values
        return [p for p in available_people if p in qualified]
        
    def check_role_conflicts(self, role: str, assigned_roles: Dict[str, List[str]]) -> Set[str]:
        """
        Check for role conflicts with current assignments.
        
        Args:
            role (str): The role to check
            assigned_roles (Dict[str, List[str]]): Current role assignments
            
        Returns:
            Set[str]: Set of people with conflicts
        """
        requirements = self.get_role_requirements(role)
        conflicts = requirements.get('conflicts', [])
        
        conflicted_people = set()
        for conflict_role in conflicts:
            if conflict_role in assigned_roles:
                conflicted_people.update(assigned_roles[conflict_role])
                
        return conflicted_people
        
    def find_best_matches(self, 
                         role: str,
                         available_people: List[str],
                         assigned_roles: Dict[str, List[str]] = None) -> List[str]:
        """
        Find best matches for a role from available people.
        
        Args:
            role (str): The role to fill
            available_people (List[str]): List of available people
            assigned_roles (Dict[str, List[str]], optional): Current role assignments
            
        Returns:
            List[str]: List of best matched people
        """
        if assigned_roles is None:
            assigned_roles = {}
            
        # Get qualified people
        qualified_people = self.get_qualified_people(role, available_people)
        
        # Remove people with conflicts
        conflicts = self.check_role_conflicts(role, assigned_roles)
        qualified_people = [p for p in qualified_people if p not in conflicts]
        
        # Get role requirements
        requirements = self.get_role_requirements(role)
        max_people = requirements.get('max_people', 1)
        
        # Return up to max_people
        return qualified_people[:max_people]
        
    def get_role_coverage(self, 
                         available_people: List[str],
                         assigned_roles: Dict[str, List[str]] = None) -> Dict[str, float]:
        """
        Calculate coverage percentage for each role.
        
        Args:
            available_people (List[str]): List of available people
            assigned_roles (Dict[str, List[str]], optional): Current role assignments
            
        Returns:
            Dict[str, float]: Dictionary mapping roles to coverage percentage
        """
        coverage = {}
        for role in self.role_requirements:
            qualified = self.get_qualified_people(role, available_people)
            requirements = self.get_role_requirements(role)
            min_required = requirements.get('min_people', 1)
            
            if min_required == 0:
                coverage[role] = 100.0
            else:
                coverage[role] = (len(qualified) / min_required * 100)
                
        return coverage