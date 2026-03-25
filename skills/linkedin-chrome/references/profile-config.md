# LinkedIn Profile Configuration

## Profile URL

LinkedIn username: `matthias-goodman-3a36961a0`

Activity page: `https://www.linkedin.com/in/matthias-goodman-3a36961a0/recent-activity/all/`

## Finding the Profile URL

If the username changes or you need to verify, navigate to `https://www.linkedin.com/feed/` and run:

```javascript
document.querySelector('a[href*="/in/"]').href
```
