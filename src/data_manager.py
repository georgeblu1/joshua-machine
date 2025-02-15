import pandas as pd
import pygsheets
import streamlit as st
from typing import Dict, Optional, List, Union
from enum import Enum

class DataSource(Enum):
    GOOGLE_SHEETS = "google_sheets"
    EXCEL = "excel"

class DataManager:
    """Handles data operations from both Google Sheets and Excel files."""
    
    def __init__(self):
        """Initialize DataManager."""
        self.source_type = None
        self.gc = None
        self.sheet = None
        self.excel_file = None
        self.cached_data: Dict[str, pd.DataFrame] = {}
        
    def initialize_google_sheets(self, credentials_path: str) -> None:
        """Initialize Google Sheets connection."""
        self.gc = pygsheets.authorize(service_file=credentials_path)
        
    def connect_to_source(self, source_type: DataSource, **kwargs) -> bool:
        """
        Connect to data source (Google Sheets or Excel).
        
        Args:
            source_type: Type of data source
            **kwargs: Source-specific arguments (sheet_key for Google Sheets,
                     file_data for Excel)
        """
        try:
            self.source_type = source_type
            if source_type == DataSource.GOOGLE_SHEETS:
                if not self.gc:
                    raise ValueError("Google Sheets not initialized")
                self.sheet = self.gc.open_by_key(kwargs.get('sheet_key'))
            elif source_type == DataSource.EXCEL:
                excel_data = kwargs.get('file_data')
                if excel_data is None:
                    raise ValueError("No Excel file provided")
                self.excel_file = pd.ExcelFile(excel_data)
            else:
                raise ValueError(f"Unsupported data source: {source_type}")
                
            # Verify required sheets exist
            self._verify_sheets()
            return True
            
        except Exception as e:
            st.error(f"Error connecting to {source_type}: {str(e)}")
            return False
            
    def _verify_sheets(self) -> None:
        """Verify all required sheets exist."""
        required_sheets = {
            "cleaned_availability",
            "vocal_main",
            "vocal_sub",
            "piano",
            "drum",
            "bass",
            "pa",
            "ppt",
            "final_schedule"
        }
        
        if self.source_type == DataSource.GOOGLE_SHEETS:
            available_sheets = {ws.title for ws in self.sheet.worksheets()}
        else:  # Excel
            available_sheets = set(self.excel_file.sheet_names)
            
        missing_sheets = required_sheets - available_sheets
        if missing_sheets:
            raise ValueError(f"Missing required sheets: {missing_sheets}")
            
    def get_worksheet(self, title: str) -> Optional[pd.DataFrame]:
        """Get data from a specific worksheet."""
        try:
            if title in self.cached_data:
                return self.cached_data[title]
                
            if self.source_type == DataSource.GOOGLE_SHEETS:
                wks = self.sheet.worksheet_by_title(title)
                df = wks.get_as_df()
            else:  # Excel
                df = pd.read_excel(self.excel_file, sheet_name=title)
                
            # Clean the data
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            self.cached_data[title] = df
            return df
            
        except Exception as e:
            st.error(f"Error getting worksheet {title}: {str(e)}")
            return None
            
    def save_worksheet(self, title: str, data: pd.DataFrame) -> bool:
        """Save data to a specific worksheet."""
        try:
            if self.source_type == DataSource.GOOGLE_SHEETS:
                wks = self.sheet.worksheet_by_title(title)
                wks.clear('A1', None, '*')
                wks.set_dataframe(data, (0,0), encoding='utf-8', fit=True)
            else:  # Excel
                # For Excel, we'll need to create a new file with all sheets
                with pd.ExcelWriter('updated_schedule.xlsx') as writer:
                    # Copy all existing sheets except the one being updated
                    for sheet_name in self.excel_file.sheet_names:
                        if sheet_name != title:
                            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    # Write the updated sheet
                    data.to_excel(writer, sheet_name=title, index=False)
                st.success("Schedule saved to 'updated_schedule.xlsx'")
                
            self.cached_data[title] = data
            return True
            
        except Exception as e:
            st.error(f"Error saving to worksheet {title}: {str(e)}")
            return False
            
    def get_availability_data(self) -> Optional[pd.DataFrame]:
        """Get and clean availability data."""
        df = self.get_worksheet("cleaned_availability")
        if df is not None:
            df = df.replace({
                'Yes': 'Yes', 'yes': 'Yes', 'YES': 'Yes',
                'No': 'No', 'no': 'No', 'NO': 'No'
            })
        return df
        
    def get_role_data(self, role_titles: List[str]) -> Dict[str, pd.DataFrame]:
        """Get data for specific roles."""
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
        """Get the final schedule data."""
        return self.get_worksheet("final_schedule")
        
    def save_final_schedule(self, schedule: pd.DataFrame) -> bool:
        """Save the final schedule."""
        return self.save_worksheet("final_schedule", schedule)