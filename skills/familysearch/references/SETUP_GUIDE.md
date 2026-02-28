# FamilySearch Developer Setup Guide

## 1. Create a Developer Account

1. Go to [FamilySearch Developer Center](https://www.familysearch.org/developers/)
2. Sign in with your FamilySearch account (or create one)
3. Apply for the **Innovator Program**
4. Wait for acceptance email (typically 1-2 weeks)

## 2. Register Your Application

Once accepted into the Innovator Program:

1. Go to the [Solutions Community](https://www.familysearch.org/developers/docs/guides/getting-started)
2. Click **"Register App"**
3. Fill in:
   - **Solution Name**: Your project name (e.g., "Goodman Family History Research")
   - **App Type**: Desktop
   - **Redirect URI**: `http://localhost:8765/callback`
4. Save your **App Key** — you'll need it in step 3

## 3. Configure Local Credentials

Run the config command to store your app key:

```bash
python3 scripts/familysearch.py config \
  --app-key "YOUR_APP_KEY_HERE" \
  --redirect-uri "http://localhost:8765/callback" \
  --env integration
```

This creates `~/.familysearch/config.json`.

## 4. Authenticate

```bash
python3 scripts/familysearch.py auth
```

This will:

1. Start a local HTTP server on port 8765
2. Open your browser to the FamilySearch OAuth2 login page
3. After you log in, FamilySearch redirects back to `localhost:8765/callback`
4. The script exchanges the authorization code for access + refresh tokens
5. Tokens are saved to `~/.familysearch/token.json`

### Integration Environment Credentials

For the sandbox (integration) environment, use the test account credentials you received when registering as a developer. These are separate from your regular FamilySearch login.

## 5. Verify

```bash
python3 scripts/familysearch.py verify
```

Expected output:

```json
{
  "status": "ok",
  "environment": "integration",
  "user": "Test User",
  "personId": "XXXX-XXX"
}
```

## 6. Switch to Production (After Approval)

Once your app passes the Compatible Solution Program review:

```bash
python3 scripts/familysearch.py config --env production
python3 scripts/familysearch.py auth
python3 scripts/familysearch.py verify
```

## Troubleshooting

### "401 Unauthorized" on every request

Your access token has expired (2-hour lifetime). The script auto-refreshes, but if the refresh token is also expired, re-run `auth`:

```bash
python3 scripts/familysearch.py auth
```

### "403 Forbidden" on production endpoints

Your app key isn't enabled for production yet. Use `--env integration` to work against the sandbox while waiting for approval.

### Port 8765 already in use

Change the redirect port:

```bash
python3 scripts/familysearch.py config --redirect-uri "http://localhost:9876/callback"
python3 scripts/familysearch.py auth
```

Update your app's redirect URI in the FamilySearch developer portal to match.
