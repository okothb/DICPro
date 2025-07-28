# Document Integrity Protection System - Web Application

A modern web interface for the Document Integrity Protection System, built with Flet.

## Features

### 🔐 Authentication
- **Social Login**: Google, GitHub, Apple (placeholder implementation)
- **No Email/Password**: Streamlined authentication experience
- **Session Management**: Secure user sessions

### 🛡️ Document Protection
- **Encryption**: AES-256 encryption for secure document protection
- **Hashing**: SHA-256 hashing for document integrity verification
- **Verification**: Comprehensive integrity checking and reporting

### 💎 Premium Features (Coming Soon)
- **Paywall Integration**: Placeholder for subscription management
- **Unlimited Access**: Advanced features for premium users
- **Priority Support**: Enhanced customer support

## Quick Start

### Prerequisites
- Python 3.8 or higher
- All dependencies from `requirements.txt`

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the web application:
   ```bash
   python start_web_app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8550
   ```

## Usage

### Landing Page
- **Public Access**: No authentication required
- **Feature Overview**: Learn about the system's capabilities
- **Get Started**: Begin the authentication process

### Dashboard
- **Welcome Screen**: Personalized greeting
- **Quick Stats**: Overview of your activity
- **Quick Actions**: Direct access to main features

### Encryption Page
1. Click "Choose File" to select a document
2. Enter a strong encryption password
3. Click "Encrypt Document" to secure your file
4. Download the encrypted file

### Hashing Page
1. Click "Choose File" to select a document
2. Click "Generate Hash" to create a SHA-256 hash
3. View the generated hash value
4. Hash is automatically saved for future verification

### Verification Page
1. Click "Choose File" to select a document
2. Click "Verify Integrity" to check document integrity
3. View verification results
4. Access detailed integrity reports

### Settings Page
- **Account Information**: View your profile details
- **Subscription Status**: Check your current plan
- **Upgrade Options**: Access premium features (placeholder)

## Architecture

### Core Integration
The web application integrates directly with your existing core modules:
- `core/encryptor.py` - Document encryption functionality
- `core/hash_generator.py` - Hash generation and storage
- `core/verifier.py` - Document verification and integrity checking

### UI Framework
- **Flet**: Modern Python UI framework
- **Responsive Design**: Works on desktop and mobile browsers
- **Material Design**: Clean, professional interface

### Authentication Flow
1. **Landing Page** → Public access
2. **Social Login** → Google/GitHub/Apple (simulated)
3. **Dashboard** → Protected access to features
4. **Session Management** → Secure user state

## File Structure

```
DICPro/
├── web_app.py              # Main web application
├── start_web_app.py        # Launcher script
├── WEB_APP_README.md       # This file
├── core/                   # Core functionality (unchanged)
├── utils/                  # Utilities (unchanged)
└── data/                   # Data storage (unchanged)
```

## Development

### Adding New Features
1. **Core Integration**: Add functionality to core modules
2. **UI Components**: Create new pages in `web_app.py`
3. **Navigation**: Update navigation rail in `_init_ui_components()`
4. **Testing**: Test with various file types and scenarios

### Authentication Integration
To implement real social authentication:
1. Set up OAuth applications with providers
2. Replace `_authenticate()` method with real OAuth flow
3. Add proper session management and security
4. Implement user database/storage

### Paywall Integration
To implement subscription management:
1. Set up payment processing (Stripe, PayPal, etc.)
2. Replace `_show_paywall()` with real payment flow
3. Add subscription validation logic
4. Implement feature access control

## Security Considerations

### File Handling
- Files are processed locally
- No files are uploaded to external servers
- Temporary files are cleaned up automatically
- Encryption keys are not stored

### Authentication
- Session-based authentication
- No password storage required
- Social login tokens handled securely
- Automatic session timeout

### Data Privacy
- All processing happens locally
- No document content is transmitted
- Hash values are stored locally only
- User data is minimal and secure

## Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -r requirements.txt
```

**Port Already in Use**
- The application will automatically find an available port
- Check the console output for the correct URL

**File Upload Issues**
- Ensure file types are supported
- Check file size limits
- Verify file permissions

**Authentication Issues**
- Current implementation uses simulated authentication
- Real OAuth integration requires provider setup

## Support

For issues or questions:
1. Check the main project documentation
2. Review the core module documentation
3. Check the console for error messages
4. Verify all dependencies are installed

## License

This web application is part of the Document Integrity Protection System and follows the same license terms as the main project. 