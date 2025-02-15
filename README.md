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

## Google Sheets Setup

1. Create a Google Cloud Project:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Sheets API

2. Create Service Account:
   - Go to Credentials
   - Create Service Account
   - Download JSON credentials

3. Setup Credentials:
   - Rename downloaded JSON to `credentials.json`
   - Place in project root directory

4. Prepare Google Sheet:
   - Create new Google Sheet
   - Add required worksheets:
     - `cleaned_availability`
     - `vocal_main`
     - `vocal_sub`
     - `piano`
     - `drum`
     - `bass`
     - `pa`
     - `ppt`
     - `final_schedule`
   - Share sheet with service account email

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