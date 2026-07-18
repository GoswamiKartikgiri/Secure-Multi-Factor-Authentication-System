# 🔐 Secure Multi-Factor Authentication System

> A secure Multi-Factor Authentication (MFA) web application developed using **Flask** and **MySQL**, implementing modern authentication mechanisms including **Google Authenticator (TOTP)**, **Email OTP Verification**, secure password management, and an **Admin Dashboard**.

---

## 📌 Project Overview

This project is designed to enhance web application security by implementing multiple authentication layers. It combines traditional username/password authentication with Time-based One-Time Passwords (TOTP) and Email OTP verification to provide stronger protection against unauthorized access.

The application also includes security monitoring, login activity logging, account lockout protection, recovery codes, password reset functionality, and an administrative dashboard for user management and analytics.

---

## ✨ Features

### 🔐 Authentication

- User Registration
- Secure Login
- Logout
- Password Hashing
- Password Reset
- Change Password

### 🛡 Multi-Factor Authentication

- Google Authenticator (TOTP)
- QR Code Generation
- Email OTP Verification
- Recovery Codes
- 2FA Login Verification

### 👤 User Management

- User Profile
- Edit Profile
- Account Management

### 📊 Admin Dashboard

- Admin Login
- User Management
- Login Logs
- Security Analytics
- CSV Export
- System Settings

### 🚨 Security Features

- Account Lockout Protection
- Security Logging
- Session Management
- CSRF Protection
- Form Validation
- Secure Password Storage

---

# 🛠 Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Flask | Web Framework |
| MySQL | Database |
| SQLAlchemy | ORM |
| Flask-Login | Authentication |
| Flask-WTF | Form Handling |
| PyOTP | TOTP Authentication |
| QRCode | QR Generation |
| HTML5 | Frontend |
| CSS3 | Styling |
| JavaScript | Client-side Interaction |

---

# 📁 Project Structure

```
Secure-Multi-Factor-Authentication-System
│
├── routes/
│   ├── admin.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── email_otp.py
│   └── twofa.py
│
├── templates/
├── static/
│
├── utils/
│   ├── email_sender.py
│   ├── qr_generator.py
│   ├── recovery_code_generator.py
│   └── security_logger.py
│
├── app.py
├── config.py
├── extensions.py
├── forms.py
├── models.py
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/GoswamiKartikgiri/Secure-Multi-Factor-Authentication-System.git
```

Move into the project

```bash
cd Secure-Multi-Factor-Authentication-System
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Configure environment variables

Create a `.env` file and configure:

```
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_app_password
```

Run the application

```bash
python app.py
```

---

# 🔒 Security Mechanisms

- Password Hashing
- Google Authenticator TOTP
- Email OTP Verification
- Recovery Codes
- Account Lockout
- Login Activity Monitoring
- Secure Session Handling
- CSRF Protection

---

# 📸 Application Modules

- Home
- Register
- Login
- Dashboard
- User Profile
- Google Authenticator Setup
- Email OTP Verification
- Recovery Codes
- Password Reset
- Admin Dashboard
- Analytics
- Security Logs

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Multi-Factor Authentication (MFA)
- Authentication & Authorization
- Secure Session Management
- Web Security Best Practices
- Flask Backend Development
- Database Integration
- User Access Control
- Security Logging

---

# 🚀 Future Enhancements

- SMS OTP
- OAuth Login (Google/GitHub)
- JWT Authentication
- Docker Deployment
- REST API
- Redis Session Storage
- CAPTCHA Integration
- Audit Reports

---

# 👨‍💻 Author

**Goswami KartikGiri**

🎓 M.Sc. Cyber Security & Digital Forensics

📧 Email:
goswamikartikgiri1@gmail.com

🔗 LinkedIn:
https://www.linkedin.com/in/goswami-kartikgiri

💻 GitHub:
https://github.com/GoswamiKartikgiri

---

# 📄 License

This project is intended for educational and learning purposes.
