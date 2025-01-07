import streamlit as st
import pandas as pd
import numpy as np
import pygsheets
import random
import altair as alt
from datetime import datetime

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

def main():
    st.title("Joshua Machine")
    st.subheader("Connaught Church Service Scheduler")
    
    # Initialize session states
    if 'sheet_key' not in st.session_state:
        st.session_state.sheet_key = None
    if 'generated_schedule' not in st.session_state:
        st.session_state.generated_schedule = None
    if 'availability_data' not in st.session_state:
        st.session_state.availability_data = None
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = None
    if 'final_schedule' not in st.session_state:
        st.session_state.final_schedule = None
    if 'role_data_loaded' not in st.session_state:
        st.session_state.role_data_loaded = False

    # Configuration: Input Google Sheet key once
    if st.session_state.sheet_key is None:
        st.subheader("Google Sheet Connection")
        credentials_path = "credentials.json"
        sheet_key = st.text_input("Enter Google Sheet Key")

        if st.button("Connect to Google Sheet"):
            scheduler = ChurchScheduler(credentials_path)
            if scheduler.connect_to_sheet(sheet_key):
                st.session_state.sheet_key = sheet_key
                st.session_state.scheduler = scheduler
                availability_data = scheduler.load_availability_data()
                if availability_data is not None:
                    st.session_state.availability_data = availability_data
                    st.success("Successfully connected to Google Sheet and loaded availability data!")
                else:
                    st.error("Failed to load availability data.")
            else:
                st.error("Failed to connect to the Google Sheet.")
    else:
        st.success(f"Connected to Google Sheet: {st.session_state.sheet_key}")
        scheduler = st.session_state.scheduler
        availability_data = st.session_state.availability_data

    # Navigation tabs
    st.sidebar.header("Navigation")
    selected_tab = st.sidebar.radio(
        "Choose a tab:",
        ["Scheduling", "Analytics", "Check Availability"]
    )

    # Tab: Scheduling
    if selected_tab == "Scheduling":
        if st.session_state.scheduler is not None:
            if st.session_state.availability_data is not None:
                st.subheader("Current Availability Data")
                st.dataframe(st.session_state.availability_data)
                if st.session_state.scheduler.load_role_data():
                    st.session_state.role_data_loaded = True
                    st.success("Role data loaded successfully!")

            if st.session_state.role_data_loaded:
                if st.button("Generate Schedule", key="generate_button"):
                    with st.spinner("Generating schedule..."):
                        schedule = st.session_state.scheduler.generate_schedule()
                        if schedule is not None:
                            st.session_state.generated_schedule = schedule
                            st.success("Schedule generated successfully!")
                        else:
                            st.error("Failed to generate schedule!")

            if st.session_state.generated_schedule is not None:
                st.subheader("Generated Schedule")
                st.dataframe(st.session_state.generated_schedule)

                # Add password input for saving
                password = st.text_input("Enter password to save the schedule:", type="password", key="save_password")
                
                if password == "123456":
                    st.success("Password accepted. You can now save the schedule.")
                    if st.button("Save Schedule to Google Sheet", key="save_button"):
                        # Uncomment and replace with actual save logic
                        # if st.session_state.scheduler.save_schedule(st.session_state.generated_schedule):
                        st.success("Schedule successfully saved to Google Sheet!")
                elif password != "":
                    st.error("Incorrect password. Please try again.")

            


    # Tab: Analytics
    elif selected_tab == "Analytics":
        st.subheader("Overall Availability")
        if st.session_state.availability_data is not None:
            # Convert date columns to datetime and sort
            availability_data = st.session_state.availability_data.copy()
            date_columns = availability_data.columns[1:]  # Exclude the first column ("Name List")

            # Append the current year to the date columns for proper parsing
            current_year = datetime.now().year
            formatted_dates =  f"{current_year}/" + date_columns # Add year to "DD/MM" format

            
            # Convert to datetime
            sorted_dates = pd.to_datetime(formatted_dates, format="%Y/%d/%m", errors="coerce").sort_values()

            sorted_column_names = ["Name List"] + sorted_dates.strftime("%d/%m").tolist()

            availability_data = availability_data[sorted_column_names]
            
            # Summarize availability
            availability_summary = availability_data.iloc[:, 1:].apply(
                lambda x: (x == 'Yes').sum(), axis=0
            ).reset_index()

            availability_summary.columns = ["Date", "Count"]

            # Add a datetime version of the date for proper Altair sorting
            availability_summary["Date_dt"] = pd.to_datetime(
                f"{current_year}/" + availability_summary["Date"], format="%Y/%d/%m"
            )

            # Plot using Altair
            bar_chart = alt.Chart(availability_summary).mark_bar().encode(
                x=alt.X("Date:N", title="Date", sort=sorted_dates.strftime("%d/%m").tolist()),
                y=alt.Y("Count:Q", title="Number of Available People"),
                tooltip=["Date", "Count"],
            ).properties(
                width=1500,
                height=400,
                title="Availability Overview (Individual Dates)"
            )

            # Display the chart
            st.altair_chart(bar_chart, use_container_width=True)
            
            # Melt data for detailed analysis
            melted_df = availability_data.melt(
                id_vars=["Name List"], 
                var_name="Date", 
                value_name="Availability"
            )
            melted_df["Date"] = pd.to_datetime(melted_df["Date"], format="%Y-%m-%d", errors="coerce")

            # Group by Name List and Availability, then count occurrences
            grouped = melted_df.groupby(["Name List", "Availability"]).size().unstack(fill_value=0)
            grouped = grouped.sort_values(by="Yes", ascending=False)

            # Prepare the data for Altair visualization
            chart_data = grouped.reset_index()
            chart_data_melted = chart_data.melt(
                id_vars="Name List", 
                value_vars=["Yes", "No"], 
                var_name="Availability", 
                value_name="Count"
            )

            # Plot the stacked bar chart using Altair
            bar_chart = alt.Chart(chart_data_melted).mark_bar().encode(
                x=alt.X("Count:Q", stack="normalize", title="Count (Normalized)"),
                y=alt.Y(
                    "Name List:N", 
                    sort="-x",  # Sort by total count of "Yes"
                    title="Person"
                ),
                color=alt.Color(
                    "Availability:N", 
                    scale=alt.Scale(domain=["Yes", "No"], range=["#1f77b4", "#d62728"])
                ),
                tooltip=["Name List", "Availability", "Count"]
            ).properties(
                width=1500,
                height=max(30 * len(grouped), 500),  # Dynamically adjust height based on the number of rows
                title="Availability Count per Person (Ordered by Sum of Yes)"
            )

            # Display the chart
            st.altair_chart(bar_chart, use_container_width=True)

            st.subheader("Role Coverage Insights")
            # Load final schedule data using existing scheduler instance
            if st.session_state.scheduler is not None:
                final_schedule = st.session_state.scheduler.load_final_schedule_data()
                if final_schedule is not None:
                    st.session_state.final_schedule = final_schedule
                else:
                    st.warning("Could not load final schedule data.")
            
            # Use the loaded final schedule data
            if st.session_state.final_schedule is not None:
                # Copy the schedule data
                scheduled_data = st.session_state.final_schedule.copy()

                # Reshape the data: Convert wide format to long format
                melted_schedule = scheduled_data.melt(
                    id_vars=["role"],  # Keep "role" as the identifier
                    var_name="Date",   # Columns become "Date"
                    value_name="Person"  # Values become "Person"
                ).dropna()

                # Ensure uniform data types and handle "None"/NaN
                melted_schedule["Person"] = melted_schedule["Person"].fillna("Unassigned")

                # Analytics: Assignments per Person
                st.subheader("Assignments per Person")
                person_assignments = melted_schedule.groupby("Person").size().reset_index(name="Count")
                person_chart = alt.Chart(person_assignments).mark_bar().encode(
                    x=alt.X("Person:N", sort="-y", title="Person"),
                    y=alt.Y("Count:Q", title="Number of Assignments"),
                    tooltip=["Person", "Count"]
                ).properties(
                    width=800,
                    height=400,
                    title="Assignments per Person"
                )
                st.altair_chart(person_chart, use_container_width=True)

                # Analytics: Assignments per Role
                st.subheader("Assignments per Role")
                role_assignments = melted_schedule.groupby("role").size().reset_index(name="Count")
                role_chart = alt.Chart(role_assignments).mark_bar().encode(
                    x=alt.X("role:N", sort="-y", title="Role"),
                    y=alt.Y("Count:Q", title="Number of Assignments"),
                    tooltip=["role", "Count"]
                ).properties(
                    width=800,
                    height=400,
                    title="Assignments per Role"
                )
                st.altair_chart(role_chart, use_container_width=True)

                # Analytics: Fairness Analysis
                st.subheader("Fairness Analysis")
                avg_assignments = person_assignments["Count"].mean()
                person_assignments["Deviation"] = person_assignments["Count"] - avg_assignments
                fairness_chart = alt.Chart(person_assignments).mark_bar().encode(
                    x=alt.X("Person:N", sort="-y", title="Person"),
                    y=alt.Y("Deviation:Q", title="Deviation from Average"),
                    color=alt.condition(
                        alt.datum.Deviation > 0,
                        alt.value("#1f77b4"),  # Blue for above average
                        alt.value("#d62728")  # Red for below average
                    ),
                    tooltip=["Person", "Count", "Deviation"]
                ).properties(
                    width=800,
                    height=400,
                    title="Deviation from Average Assignments"
                )
                st.altair_chart(fairness_chart, use_container_width=True)

            else:
                st.info("No final schedule data available for analysis.")
        else:
            st.error("Scheduler not properly initialized.")



                
            
        


    # Tab: Check Availability for a Specific Date
    elif selected_tab == "Check Availability":
        st.subheader("Check Availability for a Specific Date")
        
        if st.session_state.availability_data is not None:
            # Let the user select a date
            available_dates = st.session_state.availability_data.columns[1:]  # Exclude the Name List column
            selected_date = st.selectbox("Select a Date to Check Availability", available_dates)
            
            if selected_date:
                # Filter the data for the selected date
                available_people = st.session_state.availability_data[
                    st.session_state.availability_data[selected_date] == "Yes"
                ]["Name List"].tolist()
                
                if available_people:
                    # Create a table showing who is available for each role
                    role_availability = {}
                    
                    for role in st.session_state.scheduler.sheet_titles:

                        # Get people qualified for this role
                        qualified_people = st.session_state.scheduler.dataframes[role]["name"].values
                        
                        # Intersect with available people
                        available_for_role = list(set(available_people) & set(qualified_people))
                        role_availability[role] = ", ".join(available_for_role) if available_for_role else "None"
                    
                    # Convert the dictionary to a DataFrame for display
                    availability_df = pd.DataFrame.from_dict(
                        role_availability, orient="index", columns=["Available People"]
                    )
                    availability_df.index.name = "Role"
                    
                    # Display the table
                    st.table(availability_df)
                else:
                    st.warning(f"No one is available on {selected_date}.")
        else:
            st.info("Please load availability data first.")



if __name__ == "__main__":
    main()