# Authentication Setup Guide

This document provides comprehensive instructions for setting up and managing the authentication system in the AI Agents web application.

## Table of Contents
1. [How the Authentication System Works](#how-the-authentication-system-works)
2. [Default Admin Credentials](#default-admin-credentials)
3. [Creating New Users](#creating-new-users)
4. [Security Best Practices](#security-best-practices)
5. [Password Requirements](#password-requirements)
6. [Session Timeout Settings](#session-timeout-settings)

---

## How the Authentication System Works

The authentication system is built on industry-standard security practices:

### Architecture
- **Authentication Method**: Session-based authentication with secure HTTP-only cookies
- **Password Storage**: All passwords are hashed using bcrypt with a salt factor of 12
- **Token Management**: JWT (JSON Web Tokens) are used for API authentication
- **Session Storage**: Sessions are stored server-side with encrypted session data

### Authentication Flow
1. User submits credentials (username/email and password)
2. Server verifies credentials against the database
3. If valid, server creates a secure session and issues a session token
4. Session token is stored in an HTTP-only cookie
5. Subsequent requests include the session token for authentication
6. Server validates the token on each protected endpoint

### Security Features
- CSRF protection enabled on all state-changing operations
- Rate limiting to prevent brute-force attacks (5 failed attempts per 15 minutes)
- Automatic account lockout after 5 consecutive failed login attempts
- Password reset functionality with time-limited tokens (valid for 1 hour)
- Two-factor authentication support (optional)

---

## Default Admin Credentials

**⚠️ IMPORTANT: Change these credentials immediately after first deployment!**

### Initial Admin Account
```
Username: admin
Email: admin@localhost
Password: ChangeMe123!
```

### First-Time Setup Steps
1. Log in using the default credentials
2. Navigate to **Settings** → **Account** → **Change Password**
3. Set a strong, unique password following the password requirements below
4. Update the admin email address to a valid email
5. Enable two-factor authentication (recommended)

### Post-Setup Verification
- Verify you can log in with the new credentials
- Test the password reset functionality
- Ensure old credentials no longer work

---

## Creating New Users

### Method 1: Admin Dashboard (Recommended)
1. Log in as an administrator
2. Navigate to **Admin Panel** → **User Management**
3. Click **Add New User**
4. Fill in the required fields:
   - Username (3-30 characters, alphanumeric and underscores only)
   - Email address (must be valid and unique)
   - Full name
   - Role (User, Moderator, or Admin)
5. Choose one of the following:
   - **Auto-generate password**: System generates a secure password and emails it to the user
   - **Set temporary password**: Enter a temporary password (user must change on first login)
6. Click **Create User**

### Method 2: Self-Registration (If Enabled)
1. Users visit the `/register` endpoint
2. Fill in the registration form
3. Verify email address via confirmation link
4. Account is activated after email verification
5. Admin can optionally approve new registrations from the dashboard

### Method 3: CLI Tool
For bulk user creation or scripting:
```bash
python manage_users.py create \
  --username "newuser" \
  --email "user@example.com" \
  --full-name "New User" \
  --role "user"
```

### User Roles and Permissions
- **User**: Basic access to application features
- **Moderator**: User permissions + content moderation capabilities
- **Admin**: Full system access including user management and configuration

---

## Security Best Practices

### For Administrators
1. **Change Default Credentials**: Always change default admin credentials before going live
2. **Regular Audits**: Review user accounts and access logs monthly
3. **Principle of Least Privilege**: Grant users the minimum permissions necessary
4. **Enable 2FA**: Require two-factor authentication for all admin accounts
5. **Monitor Failed Logins**: Set up alerts for unusual login patterns
6. **Keep Software Updated**: Regularly update dependencies and security patches
7. **Backup Authentication Data**: Maintain encrypted backups of user data
8. **Use HTTPS**: Always deploy with valid SSL/TLS certificates
9. **Secure Session Storage**: Use secure, encrypted session storage in production
10. **Review Access Regularly**: Disable inactive accounts after 90 days

### For Users
1. **Strong Passwords**: Use unique, complex passwords (see requirements below)
2. **Enable 2FA**: Activate two-factor authentication if available
3. **Secure Devices**: Only log in from trusted devices
4. **Log Out**: Always log out from shared or public computers
5. **Monitor Activity**: Review login history regularly for suspicious activity
6. **Report Issues**: Immediately report any security concerns to administrators

### Environment Variables
Ensure the following environment variables are properly configured:
```bash
SECRET_KEY=<strong-random-secret-key>  # Generate using: openssl rand -hex 32
SESSION_SECRET=<session-secret-key>    # Generate using: openssl rand -hex 32
DATABASE_ENCRYPTION_KEY=<encryption-key> # For encrypting sensitive data
JWT_SECRET_KEY=<jwt-secret>            # For API token signing
```

**Never commit these values to version control!**

---

## Password Requirements

All passwords must meet the following criteria:

### Minimum Requirements
- **Length**: At least 12 characters
- **Uppercase Letters**: At least 1 uppercase letter (A-Z)
- **Lowercase Letters**: At least 1 lowercase letter (a-z)
- **Numbers**: At least 1 digit (0-9)
- **Special Characters**: At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Additional Rules
- Cannot contain the username or email address
- Cannot be a commonly used password (checked against a list of 10,000+ common passwords)
- Cannot be the same as any of the last 5 passwords used
- Must be different from the default password

### Password Strength Indicator
The system provides real-time feedback during password creation:
- **Weak**: Does not meet minimum requirements (rejected)
- **Fair**: Meets minimum requirements but could be stronger
- **Good**: Strong password with good entropy
- **Excellent**: Very strong password with high entropy

### Password Expiration
- **Admin accounts**: Passwords expire every 90 days
- **Regular users**: Passwords expire every 180 days (configurable)
- Users receive email reminders 7 days before expiration

### Password Reset
1. Click "Forgot Password" on the login page
2. Enter your email address
3. Check email for password reset link (valid for 1 hour)
4. Click link and enter new password
5. Log in with new credentials

---

## Session Timeout Settings

### Default Timeouts
- **Idle Timeout**: 30 minutes of inactivity
- **Absolute Timeout**: 12 hours from login (regardless of activity)
- **Remember Me**: 30 days (if "Remember Me" is checked at login)

### Configuring Timeouts
Timeout values can be adjusted in `config/auth.py`:

```python
# Session configuration
SESSION_CONFIG = {
    'idle_timeout': 1800,      # 30 minutes in seconds
    'absolute_timeout': 43200,  # 12 hours in seconds
    'remember_me_duration': 2592000,  # 30 days in seconds
    'refresh_on_activity': True,  # Reset idle timer on user activity
}
```

### Session Management Features
- **Activity Tracking**: User activity automatically extends the idle timeout
- **Warning Notification**: Users receive a 2-minute warning before session expiration
- **Auto-Save**: Forms are auto-saved before session expiration
- **Concurrent Sessions**: Maximum 3 concurrent sessions per user (configurable)
- **Session Revocation**: Users can view and revoke active sessions from their account settings

### Session Storage
- **Development**: Sessions stored in memory or file-based storage
- **Production**: Use Redis or database-backed session storage for scalability
- **Encryption**: All session data is encrypted at rest

### Viewing Active Sessions
Users can manage their active sessions:
1. Navigate to **Settings** → **Security** → **Active Sessions**
2. View list of all active sessions with:
   - Device information
   - IP address
   - Location (approximate)
   - Login time
   - Last activity
3. Click **Revoke** to end any session remotely

---

## Troubleshooting

### Common Issues

**Cannot log in with default credentials**
- Ensure you're using the exact credentials (case-sensitive)
- Check if the admin account has already been modified
- Verify database is properly initialized

**Session expires too quickly**
- Check session timeout settings in configuration
- Ensure system time is synchronized across servers
- Verify session storage is functioning correctly

**Password reset emails not received**
- Check spam/junk folder
- Verify email server configuration in `config/email.py`
- Check application logs for email sending errors

**Account locked after failed attempts**
- Wait 15 minutes for automatic unlock, or
- Contact an administrator to manually unlock the account

### Support
For additional assistance:
- Review application logs in `logs/auth.log`
- Check the [Wiki](https://github.com/R-c-8008/ai-agents/wiki) for detailed documentation
- Submit an issue on GitHub for bugs or feature requests

---

## Changelog

### Version 1.0.0 (Initial Release)
- Implemented session-based authentication
- Added bcrypt password hashing
- Configured session timeout settings
- Created admin user management interface
- Added password requirements validation
- Implemented rate limiting and account lockout
- Added two-factor authentication support

---

*Last Updated: November 5, 2025*
