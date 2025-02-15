# Joshua Machine (Church Service Scheduler)

A universal church service scheduling tool built with Streamlit that helps churches manage their service rosters efficiently.

## 🌟 Features

- **Automated Scheduling**: Generates balanced schedules considering member availability and roles
- **Role Management**: Supports multiple roles (vocals, instruments, technical support)
- **Analytics Dashboard**: Visualize availability patterns and scheduling statistics
- **Google Sheets Integration**: Easy data management through Google Sheets
- **Fair Distribution**: Ensures balanced assignment of duties across members

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/joshua-machine.git
cd joshua-machine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Sheets:
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create service account credentials
   - Download credentials as `credentials.json`
   - Place `credentials.json` in the project root

4. Create your Google Sheet with the following worksheets:
   - `cleaned_availability`
   - `vocal_main`
   - `vocal_sub`
   - `piano`
   - `drum`
   - `bass`
   - `pa`
   - `ppt`
   - `final_schedule`

5. Set environment variables:
```bash
export SCHEDULER_PASSWORD="your_password"
```

6. Run the application:
```bash
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables

- `SCHEDULER_PASSWORD`: Password for saving schedules (default: "123456")
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google credentials file

### Google Sheet Structure

Each worksheet should follow this format:

1. `cleaned_availability`:
   - Column 1: Name List
   - Following columns: Dates (DD/MM format)
   - Values: "Yes" or "No"

2. Role sheets (`vocal_main`, `piano`, etc.):
   - Column 1: name
   - Additional columns as needed for role-specific information

## 🐳 Docker Deployment

1. Build the Docker image:
```bash
docker build -t joshua-machine .
```

2. Run the container:
```bash
docker run -p 8501:8501 \
  -e SCHEDULER_PASSWORD="your_password" \
  -v /path/to/credentials.json:/app/credentials.json \
  joshua-machine
```

## 🚀 Cloud Run Deployment

1. Build and push to Google Container Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/joshua-machine
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy joshua-machine \
  --image gcr.io/YOUR_PROJECT_ID/joshua-machine \
  --platform managed \
  --allow-unauthenticated
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/)
- [PyGSheets](https://pygsheets.readthedocs.io/)
- [Altair](https://altair-viz.github.io/)