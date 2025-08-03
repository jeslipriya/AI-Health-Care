# Flask Web Application

## Project Overview
This is a Flask-based web application featuring user authentication and AI-powered tools like a chatbot, mood tracker, health tips, and a nearby hospital finder-all powered by the Gemini API. It also supports voice input and response for a more interactive experience.

## Features
- User authentication (Login/Signup)
- Email notifications using Flask-Mail
- AI-powered responses via Gemini API
- Voice input and response support 
- Interactive map integration with Leaflet.js
- SQLite3 database for data storage

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Database:** SQLite3
- **Email Service:** Flask-Mail
- **API Integration:** Gemini API
- **Mapping:** Leaflet.js

## Setup Instructions

### Clone the Repository
```bash
git clone https://github.com/jeslipriya/AI-Health-Care.git
cd AI-Health-Care
```

### Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
flask run
```
Your app will be available at `http://127.0.0.1:5000/`

## Contributing
Pull requests are welcome! If you find any issues, feel free to open an issue or contribute.

## Contact
For any queries, reach out at: `jeslipriya07@gmail.com`

