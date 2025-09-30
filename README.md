# web-app-questionari

A Flask-based web application for creating and managing questionnaires.

## Features

- Create, read, update, and delete questionnaires
- RESTful API endpoints
- Responsive web interface
- In-memory data storage
- Easy-to-use interface

## Technology Stack

- **Backend:** Flask 3.0.0 (Python web framework)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **API:** RESTful architecture

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pablozramirez73/web-app-questionari.git
cd web-app-questionari
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Web Interface

- **Home Page** (`/`): Welcome page with feature overview
- **Questionnaires** (`/questionnaires`): View and manage questionnaires
- **About** (`/about`): Information about the application and API documentation

### API Endpoints

#### Questions/Questionnaires

- `GET /api/questions` - Get all questionnaires
- `POST /api/questions` - Create a new questionnaire
  ```json
  {
    "title": "Sample Questionnaire",
    "description": "Description here",
    "questions": []
  }
  ```
- `GET /api/questions/<id>` - Get a specific questionnaire
- `PUT /api/questions/<id>` - Update a questionnaire
- `DELETE /api/questions/<id>` - Delete a questionnaire

#### Responses

- `GET /api/responses` - Get all responses
- `POST /api/responses` - Submit a response
  ```json
  {
    "question_id": 1,
    "answers": []
  }
  ```

## Project Structure

```
web-app-questionari/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── questionnaires.html
│   └── about.html
├── static/             # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── README.md          # This file
```

## Development

The application runs in debug mode by default when started with `python app.py`. This enables:
- Auto-reload on code changes
- Detailed error pages
- Debug mode features

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.