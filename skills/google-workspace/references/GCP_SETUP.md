# Google Cloud Project Setup Guide

To use the Google Workspace skill reliably, you should set up your own Google Cloud Project. This avoids sharing quotas and ensures you control the credentials.

## 1. Create a Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Create Project**.
3. Name it something like `gemini-workspace-skill`.
4. Click **Create**.

## 2. Enable APIs
Enable the following APIs for your project via **APIs & Services > Library**:
- **Gmail API**
- **Google Calendar API**
- **Google People API** (Contacts)
- **Google Drive API**
- **Photos Library API**

## 3. Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. **User Type**:
   - **Internal**: Choose this if you use a Google Workspace account (e.g., `@yourcompany.com`). **Best option.** Tokens do not expire.
   - **External**: Must choose this for `@gmail.com` accounts.
3. Click **Create**.
4. Fill in:
   - **App Name**: `Gemini Workspace`
   - **Support Email**: Your email.
5. **Scopes**: You can skip adding scopes manually (the client handles requests dynamically), or add the sensitive scopes if you plan to verify the app (unlikely for personal use).
6. **Test Users** (External only):
   - Add your own email address.
   - **Important**: While in "Testing" mode, refresh tokens expire every **7 days**. You will need to re-authenticate weekly.

## 4. Create Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. **Application type**: **Desktop app**.
4. Name: `Desktop Client`.
5. Click **Create**.
6. **Download JSON**.
7. Rename the file to `credentials.json`.

## 5. Install Credentials
Place the `credentials.json` file in one of these locations:
- `~/.google_workspace/credentials.json` (Recommended)
- The directory where you run the scripts.

## 6. Authenticate
Run the setup script to generate your `token.json`:

```bash
uv run skills/google-workspace/scripts/setup_workspace.py
```

## Token Expiration Note
- **Internal App**: Refresh token never expires.
- **External (Production)**: Refresh token never expires (requires Google verification).
- **External (Testing)**: Refresh token expires in **7 days**.

If you are a personal Gmail user, you are stuck with "External (Testing)" unless you go through the expensive verification process. The **Token Maintainer** script helps keep the *access token* (1 hour) alive, but it cannot prevent the *refresh token* (7 days) from dying. You will simply have to re-auth weekly.
