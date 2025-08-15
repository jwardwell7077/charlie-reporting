"""setup_secure_email.py
---------------------
Setup script for secure email authentication with Google OAuth 2.0
"""

import os
import subprocess
import sys


def install_google_auth():
    """Install Google authentication libraries"""
    print("📦 Installing Google authentication libraries...")

    packages = [
        'google - auth',
        'google - auth - oauthlib',
        'google - auth - httplib2'
    ]

    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False

    print("✅ All Google authentication libraries installed!")
    return True


def create_credentials_template():
    """Create a template credentials file"""
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your - project - id",
            "auth_uri": "https://accounts.google.com / o/oauth2 / auth",
            "token_uri": "https://oauth2.googleapis.com / token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com / oauth2 / v1 / certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    demo_dir = os.path.dirname(__file__)
    config_dir = os.path.dirname(demo_dir)
    credentialspath = os.path.join(config_dir, 'credentials_template.json')

    import json
    with open(credentials_path, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"📄 Created credentials template: {credentials_path}")
    print("   Replace with your actual OAuth credentials from Google Cloud Console")


def print_setup_instructions():
    """Print detailed setup instructions"""
    print("\n" + "="*60)
    print("🔐 GOOGLE OAUTH 2.0 SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. 🌐 Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    print("2. 📁 Create or select a project")
    print()
    print("3. 🔧 Enable Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click 'Enable'")
    print()
    print("4. 🔑 Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Choose 'Desktop application'")
    print("   - Name it 'Charlie Reporting System'")
    print("   - Download the JSON file")
    print()
    print("5. 📄 Save credentials:")
    print("   - Rename downloaded file to 'credentials.json'")
    print("   - Place it in your demo folder")
    print()
    print("6. 🚀 Test with:")
    print("   python email_sender_oauth.py")
    print()
    print("="*60)


if __name__ == "__main__":
    print("🔧 Charlie Reporting - Secure Email Setup")
    print("="*50)

    # Install packages
    if install_google_auth():
        # Create template
        create_credentials_template()

        # Print instructions
        print_setup_instructions()

        print("✅ Setup complete! Follow the instructions above to configure OAuth.")
    else:
        print("❌ Setup failed. Please check your internet connection and try again.")