# Joshua Machine - Church Service Scheduler

A Streamlit-based application designed to automate the scheduling of church service roles while considering availability and role qualifications.

## Features

- **Automated Schedule Generation**: Efficiently creates service schedules based on member availability and role qualifications
- **Role-Based Assignment**: Supports multiple roles including:
  - Main Vocal
  - Sub Vocals (2 positions)
  - Piano
  - Drum
  - Bass
  - PA System
  - Presentation (PPT)
- **Fair Distribution**: Implements intelligent assignment algorithms to ensure equitable distribution of roles
- **Analytics Dashboard**: Provides insights into:
  - Overall member availability
  - Role coverage
  - Assignment distribution
  - Fairness analysis
- **Availability Checker**: Tool to check member availability for specific dates
- **Google Sheets Integration**: Seamlessly connects with Google Sheets for data management

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with Sheets API enabled
- Google Sheets API credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/joshua-machine.git
cd joshua-machine
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Sheets credentials:
   - Create a project in Google Cloud Console
   - Enable Google Sheets API
   - Create service account credentials
   - Download the credentials as `credentials.json`
   - Place `credentials.json` in the project root directory

## Google Sheets Structure

The application expects the following worksheet structure in your Google Sheet:

1. `cleaned_availability` - Member availability data
   - First column: Member names
   - Subsequent columns: Dates (DD/MM format)
   - Values: "Yes" or "No"

2. Role-specific sheets:
   - `vocal_main` - Main vocal qualified members
   - `vocal_sub` - Sub vocal qualified members
   - `piano` - Piano qualified members
   - `drum` - Drum qualified members
   - `bass` - Bass qualified members
   - `pa` - PA system qualified members
   - `ppt` - Presentation qualified members

3. `final_schedule` - Generated schedule output

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Enter your Google Sheet key in the connection panel

3. Navigate through the tabs:
   - **Scheduling**: Generate and save service schedules
   - **Analytics**: View availability and assignment statistics
   - **Check Availability**: Check member availability for specific dates

## Algorithm Details

The scheduler implements a priority-based assignment system that:
1. Considers member availability for each date
2. Checks role qualifications
3. Maintains fair distribution of assignments
4. Prevents duplicate assignments on the same date
5. Preserves role-specific requirements (e.g., separate main and sub vocals)

## Configuration

Default password for saving schedules: `123456`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [PyGSheets](https://pygsheets.readthedocs.io/) for Google Sheets integration
- Visualization powered by [Altair](https://altair-viz.github.io/)

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Sample Data

A sample Excel file (`Schedule.xlsx`) is provided to demonstrate the expected data structure. You can use this as a template when setting up your own Google Sheet.

## Security Note

The current implementation includes a hardcoded password (`123456`) for schedule saving. In a production environment, it's recommended to:
1. Use environment variables for sensitive data
2. Implement proper authentication
3. Enable HTTPS
4. Follow security best practices