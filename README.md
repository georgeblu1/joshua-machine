# Joshua Machine - Church Service Scheduler

A modular Streamlit-based application designed to automate church service role scheduling while considering member availability and role qualifications.

## Project Structure

```
joshua-machine/
├── src/
│   ├── __init__.py
│   ├── data_manager.py
│   ├── analytics/           # Analytics functionality
│   │   ├── __init__.py
│   │   ├── availability_analyzer.py
│   │   ├── schedule_analyzer.py
│   │   └── visualization.py
│   ├── availability/        # Availability checking
│   │   ├── __init__.py
│   │   ├── availability_checker.py
│   │   └── role_matcher.py
│   ├── scheduler/          # Core scheduling logic
│   │   ├── __init__.py
│   │   ├── scheduler.py
│   │   └── role_manager.py
│   └── ui/                 # User interface components
│       ├── __init__.py
│       ├── scheduling_page.py
│       ├── analytics_page.py
│       └── availability_page.py
├── app.py                  # Main application entry
├── setup.py               # Package installation setup
├── requirements.txt       # Package dependencies
└── README.md             # Documentation
```

## Features

### Core Features
- **Automated Schedule Generation**: Creates service schedules based on:
  - Member availability
  - Role qualifications
  - Historical assignments
  - Fair distribution algorithms

### Role Management
- Supports multiple roles:
  - Main Vocal
  - Sub Vocals (2 positions)
  - Piano
  - Drum
  - Bass
  - PA System
  - Presentation (PPT)

### Analytics
- **Availability Analysis**:
  - Member availability patterns
  - Date-wise availability trends
  - Weekly patterns analysis
  
- **Schedule Analysis**:
  - Assignment distribution
  - Role coverage
  - Fairness metrics
  - Member participation statistics

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with Sheets API enabled
- Google Sheets API credentials

## Installation

### Method 1: Development Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/joshua-machine.git
cd joshua-machine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

### Method 2: Installation from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/joshua-machine.git
cd joshua-machine
```

2. Build and install the package:
```bash
python setup.py install
```

### Method 3: Install Dependencies Only

If you just want to run the application without installing it as a package:

```bash
pip install -r requirements.txt
```

## Sheet Format Requirements

The application requires specific worksheet structures in either Google Sheets or Excel format. A sample file (`Schedule.xlsx`) is provided in the repository for reference.

### Required Sheets

1. `cleaned_availability` Sheet:
   - First column must be named "Name List" (contains member names)
   - Subsequent columns should be dates in DD/MM format (e.g., "04/02")
   - Values should be either "Yes" or "No"
   - Example:
     ```
     Name List  | 04/02 | 11/02 | 18/02 | 25/02
     John Smith | Yes   | No    | Yes   | Yes
     Mary Jones | No    | Yes   | Yes   | No
     ```

2. Role Qualification Sheets:
   Each role requires its own sheet with qualified members:

   - `vocal_main`:
     ```
     name
     John Smith
     Sarah Kim
     ```

   - `vocal_sub`:
     ```
     name
     Mary Johnson
     Emma Davis
     ```

   - `piano`:
     ```
     name
     David Lee
     Sarah Kim
     ```

   - `drum`:
     ```
     name
     Michael Chen
     James Brown
     ```

   - `bass`:
     ```
     name
     Daniel Wilson
     James Brown
     ```

   - `pa`:
     ```
     name
     David Lee
     Michael Chen
     ```

   - `ppt`:
     ```
     name
     Laura White
     Emma Davis
     ```

3. `final_schedule` Sheet:
   - Will be populated by the application
   - Rows represent roles
   - Columns represent dates
   - Example structure:
     ```
     role        | 04/02      | 11/02      | 18/02
     vocal_main  | John Smith | Sarah Kim  | John Smith
     vocal_sub1  | Mary Jones | Emma Davis | Mary Jones
     vocal_sub2  | Emma Davis | Mary Jones | Emma Davis
     ```

### Important Notes:

1. Column Names:
   - The name column in role sheets must be lowercase "name"
   - Date columns must be in DD/MM format
   - Name List column must be exactly "Name List"

2. Values:
   - Availability values must be "Yes" or "No" (case-sensitive)
   - Role sheets should only contain qualified members
   - Member names must be consistent across all sheets

3. Sheet Names:
   - Must match exactly as specified (case-sensitive):
     - `cleaned_availability`
     - `vocal_main`
     - `vocal_sub`
     - `piano`
     - `drum`
     - `bass`
     - `pa`
     - `ppt`
     - `final_schedule`

### Converting Excel to Google Sheets

1. Create a new Google Sheet
2. Import the sample Excel file (`Schedule.xlsx`)
3. Ensure all sheet names and column headers remain exactly the same
4. Share the sheet with your service account email

### Validation Tips

Before using the sheet:
1. Check for consistent name spelling across sheets
2. Verify date format (DD/MM)
3. Ensure "Yes"/"No" values are properly capitalized
4. Confirm all required sheets are present
5. Verify column header names match specifications

## Usage

### Running the Application

Method 1: Using installed package:
```bash
joshua-machine
```

Method 2: Using Streamlit directly:
```bash
streamlit run app.py
```

### First-Time Setup

1. Launch the application
2. Enter Google Sheet key when prompted
3. Verify connection success

### Navigation

Use the sidebar to access different features:
- **Scheduling**: Generate and manage schedules
- **Analytics**: View statistics and analysis
- **Check Availability**: Check member availability

## Development

### Setup Development Environment

1. Create development environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # If exists
```

### Running Tests

```bash
pytest tests/
```

### Code Style

Follow PEP 8 guidelines and use provided tools:
```bash
# Format code
black src/

# Check style
flake8 src/

# Check types
mypy src/
```

### Making Changes

1. Create new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and test
3. Update documentation
4. Create pull request

## Troubleshooting

### Common Issues

1. ModuleNotFoundError:
   - Ensure virtual environment is activated
   - Verify installation with `pip list`
   - Check import paths

2. Google Sheets Connection:
   - Verify credentials.json location
   - Check service account permissions
   - Confirm sheet sharing settings

3. Schedule Generation:
   - Verify data format in sheets
   - Check role requirements
   - Review availability data

### Getting Help

1. Check documentation
2. Open GitHub issue
3. Contact maintainers

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Submit pull request

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/)
- [PyGSheets](https://pygsheets.readthedocs.io/)
- [Altair](https://altair-viz.github.io/)
- [Pandas](https://pandas.pydata.org/)