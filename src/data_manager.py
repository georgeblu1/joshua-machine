import pandas as pd
import pygsheets
import streamlit as st
from typing import Dict, Optional, List

class DataManager:
    """Handles all interactions with Google Sheets and data operations."""
    
    def __init__(self, credentials_path: str):
        """
        Initialize DataManager with Google Sheets credentials.
        
        Args:
            credentials_path (str): Path to the Google Sheets credentials file
        """
        self.gc = pygsheets.authorize(service_file=credentials_path)
        self.sheet = None
        self.cached_data: Dict[str, pd.DataFrame] = {}
        
    def connect_to_sheet(self, sheet_key: str) -> bool:
        """
        Connect to a specific Google Sheet.
        
        Args:
            sheet_key (str): The Google Sheet key to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.sheet = self.gc.open_by_key(sheet_key)
            return True
        except Exception as e:
            st.error(f"Error connecting to sheet: {str(e)}")
            return False
            
    def get_worksheet(self, title: str) -> Optional[pd.DataFrame]:
        """
        Get data from a specific worksheet.
        
        Args:
            title (str): The worksheet title
            
        Returns:
            Optional[pd.DataFrame]: DataFrame containing the worksheet data
        """
        try:
            if title in self.cached_data:
                return self.cached_data[title]
                
            wks = self.sheet.worksheet_by_title(title)
            df = wks.get_as_df()
            
            # Clean the data
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            self.cached_data[title] = df
            return df
        except Exception as e:
            st.error(f"Error getting worksheet {title}: {str(e)}")
            return None
            
    def save_worksheet(self, title: str, data: pd.DataFrame) -> bool:
        """
        Save data to a specific worksheet.
        
        Args:
            title (str): The worksheet title
            data (pd.DataFrame): The data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            wks = self.sheet.worksheet_by_title(title)
            wks.clear('A1', None, '*')
            wks.set_dataframe(data, (0,0), encoding='utf-8', fit=True)
            self.cached_data[title] = data
            return True
        except Exception as e:
            st.error(f"Error saving to worksheet {title}: {str(e)}")
            return False
            
    def get_availability_data(self) -> Optional[pd.DataFrame]:
        """
        Get and clean availability data.
        
        Returns:
            Optional[pd.DataFrame]: Cleaned availability data
        """
        df = self.get_worksheet("cleaned_availability")
        if df is not None:
            # Clean the data
            df = df.replace({
                'Yes': 'Yes', 'yes': 'Yes', 'YES': 'Yes',
                'No': 'No', 'no': 'No', 'NO': 'No'
            })
        return df
        
    def get_role_data(self, role_titles: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get data for specific roles.
        
        Args:
            role_titles (List[str]): List of role worksheet titles
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping role titles to their data
        """
        role_data = {}
        for title in role_titles:
            df = self.get_worksheet(title)
            if df is not None:
                role_data[title] = df
        return role_data
        
    def clear_cache(self):
        """Clear the cached data."""
        self.cached_data.clear()
        
    def get_final_schedule(self) -> Optional[pd.DataFrame]:
        """
        Get the final schedule data.
        
        Returns:
            Optional[pd.DataFrame]: The final schedule data
        """
        return self.get_worksheet("final_schedule")
        
    def save_final_schedule(self, schedule: pd.DataFrame) -> bool:
        """
        Save the final schedule.
        
        Args:
            schedule (pd.DataFrame): The schedule to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        return self.save_worksheet("final_schedule", schedule)