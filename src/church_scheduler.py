import pandas as pd
import pygsheets
import random
import streamlit as st

class ChurchScheduler:
    def __init__(self, credentials_path):
        self.gc = pygsheets.authorize(service_file=credentials_path)
        self.sheet = None
        self.roles = ['vocal_main', 'vocal_sub1', 'vocal_sub2', 'piano', 'drum', 'bass', 'pa', 'ppt']
        self.sheet_titles = ["vocal_main", "vocal_sub", "piano", "drum", "bass", "pa", "ppt"]
        self.people = None
        self.dataframes = {}
        
    def connect_to_sheet(self, sheet_key):
        """Connect to Google Sheet using the provided key"""
        try:
            self.sheet = self.gc.open_by_key(sheet_key)
            return True
        except Exception as e:
            st.error(f"Error connecting to sheet: {str(e)}")
            return False
    
    def load_availability_data(self):
        """Load and clean availability data"""
        try:
            wks = self.sheet.worksheet_by_title("cleaned_availability")
            df = wks.get_as_df()
            
            # Drop any unnamed columns if they exist
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            # First column should be names, rest should be dates
            date_columns = df.columns[1:]  # Skip the first column which should be names
            
            # Clean the data
            df = df.replace({'Yes': 'Yes', 'yes': 'Yes', 'YES': 'Yes', 
                           'No': 'No', 'no': 'No', 'NO': 'No'})
            
            self.people = df
            return df
        except Exception as e:
            st.error(f"Error loading availability data: {str(e)}")
            return None

    def load_final_schedule_data(self):
        """Load and clean availability data"""
        try:
            final_schedule = self.sheet.worksheet_by_title("final_schedule")
            df = final_schedule.get_as_df()
        
            return df
        except Exception as e:
            st.error(f"Error loading availability data: {str(e)}")
            return None
            
    def load_role_data(self):
        """Load role-specific data"""
        try:
            for title in self.sheet_titles:
                df = self.sheet.worksheet_by_title(title).get_as_df()
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
                self.dataframes[title] = df
            return True
        except Exception as e:
            st.error(f"Error loading role data: {str(e)}")
            return False
    
    def _assign_roles_for_date(self, available_people, date, scheduled=None):
        """
        Assign roles for a date while considering past assignments
        
        Parameters:
        - available_people: List of people available for this date
        - date: Current date being scheduled
        - scheduled: DataFrame of already scheduled dates (for historical tracking)
        """
        assignments = {role: None for role in self.roles}
        assigned_people = set()
        
        def get_assignment_counts(role_sheet, people, past_schedule):
            """Calculate how many times each person has been assigned to a role"""
            if past_schedule is None or past_schedule.empty:
                return {person: 0 for person in people}
            
            counts = {}
            for person in people:
                # Count assignments in previous weeks
                count = (past_schedule.loc[role_sheet] == person).sum()
                counts[person] = count
            return counts
        
        def select_person(available_candidates, role_sheet, past_schedule):
            """Select person based on their past assignment frequency"""
            if not available_candidates:
                return None
                
            # Get historical assignment counts
            assignment_counts = get_assignment_counts(role_sheet, available_candidates, past_schedule)
            
            # Find the minimum number of assignments
            min_assignments = min(assignment_counts.values())
            
            # Get all people with the minimum number of assignments
            candidates = [p for p, count in assignment_counts.items() 
                        if count == min_assignments]
            
            # Randomly select from the candidates with minimum assignments
            return random.choice(candidates)
        
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
                
            # Get people qualified for this role
            qualified_people = [p for p in remaining_people 
                            if p in self.dataframes[sheet_name]['name'].values]
            
            if not qualified_people:
                continue
                
            if role == 'vocal_main':
                selected = select_person(qualified_people, role, scheduled)
                if selected:
                    assignments[role] = selected
                    assigned_people.add(selected)
                    
            elif role in ['vocal_sub1', 'vocal_sub2']:
                # Exclude person assigned to vocal_sub1 when assigning vocal_sub2
                if role == 'vocal_sub2' and assignments['vocal_sub1']:
                    qualified_people = [p for p in qualified_people 
                                    if p != assignments['vocal_sub1']]
                
                selected = select_person(qualified_people, role, scheduled)
                if selected:
                    assignments[role] = selected
                    assigned_people.add(selected)
                    
            else:  # Other roles
                selected = select_person(qualified_people, sheet_name, scheduled)
                if selected:
                    assignments[role] = selected
                    assigned_people.add(selected)
        
        return assignments

    def generate_schedule(self):
        """Generate the schedule based on availability and historical assignments"""
        if self.people is None:
            st.error("No availability data loaded")
            return None
            
        date_columns = self.people.columns[1:]
        scheduled = pd.DataFrame(index=self.roles, columns=date_columns)
        
        # Generate schedule sequentially, using previous assignments as history
        for date in date_columns:
            available_people = self.people[self.people[date] == 'Yes'].iloc[:, 0].tolist()
            # Pass the currently scheduled dates as history
            assignments = self._assign_roles_for_date(available_people, date, scheduled)
            
            # Update schedule
            for role, person in assignments.items():
                scheduled.at[role, date] = person
        
        return scheduled
    
    def save_schedule(self, scheduled):
        """Save the generated schedule back to Google Sheet"""
        try:
            wks_write = self.sheet.worksheet_by_title("final_schedule")
            wks_write.clear('A1', None, '*')
            # Reset index to make the roles appear as a column
            scheduled = scheduled.reset_index()
            scheduled = scheduled.rename(columns={'index': 'role'})
            wks_write.set_dataframe(scheduled, (0,0), encoding='utf-8', fit=True)
            return True
        except Exception as e:
            st.error(f"Error saving schedule: {str(e)}")
            return False