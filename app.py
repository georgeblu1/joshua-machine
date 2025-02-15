import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from src.church_scheduler import ChurchScheduler

def main():
    st.title("Joshua Machine")
    st.subheader("Church Service Scheduler")
    
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
                        if st.session_state.scheduler.save_schedule(st.session_state.generated_schedule):
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