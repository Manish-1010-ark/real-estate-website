# 🏠 Real Estate Website

A modern full-stack property listing platform built with **Flask**, **PostgreSQL**, and a responsive web interface. Browse, search, filter, and inquire about properties with a comprehensive admin dashboard for property management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.1-green.svg)

---

## 📋 Table of Contents

- [Demo & Screenshots](#-demo--screenshots)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Database Configuration](#database-configuration)
  - [Running the Application](#running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🖥️ Demo & Screenshots

### Live Demo
🔗 **[View Live Demo](your-demo-url-here)** *(Replace with your actual demo URL)*

### Screenshots

#### Home Page
![Home Page](screenshots/home.png)
*Browse featured properties with an intuitive, responsive interface*

#### Property Listings
![Property Listings](screenshots/listings.png)
*Advanced search and filtering capabilities*

#### Property Details
![Property Details](screenshots/property-detail.png)
*Detailed property information with image gallery*

#### Admin Dashboard
![Admin Dashboard](screenshots/admin-dashboard.png)
*Comprehensive property management interface*

#### Mobile Responsive
<img src="screenshots/mobile-view.png" alt="Mobile View" width="300">

*Fully responsive design across all devices*

---

## ✨ Features

### 🏡 User Features
- **Property Browsing**: Explore featured properties with high-quality images, pricing, and location details
- **Advanced Search**: Filter by price range, location, bedrooms, bathrooms, and property status
- **Property Details**: View comprehensive property information, image galleries, and virtual tours
- **Inquiry System**: Submit property inquiries with integrated contact forms
- **Responsive Design**: Seamless experience across desktop, tablet, and mobile devices

### 👨‍💼 Admin Features
- **Property Management**: Full CRUD operations for property listings
- **Inquiry Management**: View, respond to, and track user inquiries
- **Dashboard Analytics**: Property statistics and inquiry metrics
- **Image Upload**: Multi-image upload with automatic optimization
- **User Authentication**: Secure JWT-based admin authentication

### 🔧 Technical Features
- **RESTful API**: Well-structured API endpoints for all operations
- **Database Migrations**: Version-controlled database schema updates
- **Email Notifications**: Automated inquiry notifications
- **Error Handling**: Comprehensive error handling and user feedback
- **Security**: Input validation, CSRF protection, and secure authentication

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Python 3.10+, Flask 3.1.1
- **Database**: PostgreSQL (Production), SQLite (Development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Migrations**: Alembic (Flask-Migrate)
- **Email**: Flask-Mail
- **Security**: Flask-Bcrypt, Flask-CORS

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Modern CSS with Flexbox/Grid
- **Icons**: Font Awesome or similar icon library
- **Images**: Responsive image handling

### Development Tools
- **Environment**: python-dotenv for configuration
- **Testing**: Flask testing utilities
- **Code Quality**: PEP 8 compliance

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:
- **Python 3.10 or higher** - [Download Python](https://python.org/downloads/)
- **PostgreSQL** - [Download PostgreSQL](https://postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Manish-1010-ark/real-estate-website.git
   cd real-estate-website/website
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Environment Setup

1. **Create environment file**
   ```bash
   cp .env.example .env  # Or create .env manually
   ```

2. **Configure environment variables**
   ```env
   # Flask Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-super-secret-key-here
   
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/real_estate_db
   # For development with SQLite:
   # DATABASE_URL=sqlite:///real_estate.db
   
   # JWT Configuration
   JWT_SECRET_KEY=your-jwt-secret-key-here
   
   # Email Configuration (Optional)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   
   # Admin Credentials
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=admin123
   ```

### Database Configuration

1. **Create PostgreSQL database**
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database
   CREATE DATABASE real_estate_db;
   
   -- Create user (optional)
   CREATE USER real_estate_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE real_estate_db TO real_estate_user;
   ```

2. **Initialize database migrations**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Seed sample data (optional)**
   ```bash
   python seed_data.py
   ```

### Running the Application

1. **Start the development server**
   ```bash
   flask run
   # Or
   python app.py
   ```

2. **Access the application**
   - **Frontend**: http://localhost:5000
   - **Admin Dashboard**: http://localhost:5000/admin
   - **API Endpoints**: http://localhost:5000/api

3. **Default Admin Credentials**
   - Email: `admin@example.com`
   - Password: `admin123`

---

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - Admin login
- `POST /api/auth/logout` - Admin logout

### Property Endpoints
- `GET /api/properties` - Get all properties (with filtering)
- `GET /api/properties/<id>` - Get property by ID
- `POST /api/properties` - Create new property (Admin)
- `PUT /api/properties/<id>` - Update property (Admin)
- `DELETE /api/properties/<id>` - Delete property (Admin)

### Inquiry Endpoints
- `POST /api/inquiries` - Submit property inquiry
- `GET /api/inquiries` - Get all inquiries (Admin)
- `PUT /api/inquiries/<id>` - Update inquiry status (Admin)

---

## 📁 Project Structure

```
real-estate-website/
├── website/
│   ├── app.py                 # Flask application entry point
│   ├── config.py             # Configuration settings
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── property.py
│   │   ├── user.py
│   │   └── inquiry.py
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── properties.py
│   │   └── inquiries.py
│   ├── static/              # Static files
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/         # Property images
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── properties.html
│   │   ├── property_detail.html
│   │   └── admin/
│   ├── migrations/          # Database migrations
│   └── utils/               # Utility functions
├── screenshots/             # README screenshots
└── README.md               # Project documentation
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Database connection error
```
Solution: Check your DATABASE_URL in .env file and ensure PostgreSQL is running
```

**Issue**: Migration errors
```
Solution: Delete migrations folder and reinitialize:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Issue**: Port already in use
```
Solution: Kill the process or use a different port:
flask run --port=5001
```

**Issue**: Static files not loading
```
Solution: Check FLASK_ENV is set to development and clear browser cache
```

### Getting Help
- Check the [Issues](https://github.com/Manish-1010-ark/real-estate-website/issues) page
- Create a new issue with detailed information
- Contact: [your-email@example.com]

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Contributors who help improve this project
- Open source libraries that make this possible

---

**⭐ Star this repository if you found it helpful!**

---

*Last updated: July 2025*
