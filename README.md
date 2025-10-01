# Questionnaire Management System

A comprehensive Flask-based web application for creating, managing, and analyzing online questionnaires. Built with modern web technologies and featuring elegant UI, advanced analytics, and robust user management.

## 🚀 Features

### ✅ Core Functionality
- **Flask Backend**: Complete MVC architecture with Flask
- **SQLite Database**: Configured with SQLAlchemy ORM
- **User Management**: Registration, authentication, profiles, admin roles
- **Questionnaire Management**: Full CRUD operations for questionnaires
- **Question Types**: 
  - Single-choice (radio buttons)
  - Multiple-choice (checkboxes)
  - Open-ended (text areas)
  - Scale rating (1-5 stars)

### 📊 Analytics & Visualization
- **Interactive Charts**: Plotly.js integration for advanced visualizations
- **Response Timeline**: Track responses over time
- **Completion Rates**: Visual completion rate tracking
- **Question Analytics**: Individual question response statistics
- **Export Data**: CSV export functionality
- **Real-time Statistics**: Live dashboard updates

### 🎨 User Interface
- **Elegant Design**: Bootstrap 5 with custom CSS
- **Responsive Layout**: Mobile-friendly design
- **Intuitive Navigation**: User-friendly interface
- **Custom Styling**: Professional color scheme and typography

### 🔒 Security & Management
- **Advanced Logging**: Rotating file handlers with configurable levels
- **Error Management**: Custom error pages (403, 404, 500)
- **CSRF Protection**: Built-in security features
- **Admin Panel**: System administration interface
- **Email Notifications**: Optional email alerts for responses

## 🛠️ Installation

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd web-app-questionari

# Run the setup script (recommended)
python setup.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Create admin user
flask create-admin

# Run the application
python app.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📋 Configuration

Create a `.env` file with your settings:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///questionnaire_dev.db

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
SEND_EMAIL_NOTIFICATIONS=false

# Logging
LOG_LEVEL=INFO
```

## 🎯 Usage

### For Users
1. **Register/Login**: Create an account or sign in
2. **Create Questionnaires**: Use the intuitive form builder
3. **Add Questions**: Choose from 4 different question types
4. **Share**: Get shareable links for your questionnaires
5. **Monitor**: Track responses in real-time
6. **Analyze**: View detailed analytics and charts
7. **Export**: Download response data as CSV

### For Administrators
1. **User Management**: View and manage user accounts
2. **System Analytics**: Monitor overall system usage
3. **Content Moderation**: Review and manage questionnaires
4. **System Configuration**: Access advanced settings

## 📊 Analytics Features

### Dashboard Statistics
- Total questionnaires created
- Response rates and completion metrics
- User engagement analytics
- Peak response time analysis

### Chart Types
- **Line Charts**: Response timeline tracking
- **Pie Charts**: Response distribution and completion rates
- **Bar Charts**: Scale rating distributions
- **Donut Charts**: Completion vs. incomplete responses

### Data Export
- CSV format with complete response data
- Question-by-question breakdown
- Respondent information and timestamps
- Compatible with Excel and data analysis tools

## 🏗️ Architecture

### Backend Structure
```
app/
├── __init__.py          # Application factory
├── models.py            # Database models
├── utils.py             # Chart generation utilities
├── email.py             # Email notification system
├── auth/                # Authentication blueprint
├── main/                # Main application routes
├── admin/               # Admin panel
├── api/                 # API endpoints
├── errors/              # Error handlers
├── static/              # CSS, JS, images
└── templates/           # Jinja2 templates
```

### Database Models
- **User**: Authentication and profile management
- **Questionnaire**: Survey metadata and settings
- **Question**: Individual questions with type and options
- **Response**: User submissions and completion tracking
- **Answer**: Individual question responses

## 🔧 Development

### Running Tests
```bash
# Run the test suite
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=app
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## 🚀 Production Deployment

### Environment Setup
```env
FLASK_ENV=production
SECRET_KEY=strong-random-secret-key
DATABASE_URL=postgresql://user:pass@localhost/questionnaire_prod
SEND_EMAIL_NOTIFICATIONS=true
```

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure secure database credentials
- [ ] Set up email notifications
- [ ] Enable proper logging
- [ ] Configure firewall rules
- [ ] Set up regular backups

## 📦 Dependencies

### Core Framework
- Flask 2.3.3 - Web framework
- SQLAlchemy 2.0.21 - Database ORM
- Flask-Login 0.6.3 - User session management
- Flask-WTF 1.1.1 - Form handling and CSRF protection

### Data Visualization
- Plotly 5.15.0 - Interactive charts
- Matplotlib 3.7.2 - Server-side chart generation
- Pandas 2.0.3 - Data manipulation
- Chart.js (CDN) - Client-side charts

### UI Framework
- Bootstrap 5.3.0 (CDN) - Responsive design
- Bootstrap Icons (CDN) - Icon library

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Created with ❤️ using Flask, Bootstrap, and modern web technologies**