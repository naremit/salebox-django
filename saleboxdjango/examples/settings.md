```
SALEBOX = {
    'API': {
        'URL': 'your-api-domain, e.g. https://sg1.getsalebox.com',
        'KEY': 'your-pos-key',
        'LICENSE': 'your-license-key',
    },
    'IMG': {
        'POSASSETS': 'your-api-domain, e.g. https://something.cloudfront.net',
    }
}
```

```
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```
