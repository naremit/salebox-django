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
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'saleboxdjango.context_processor.salebox',
            ],
        },
    },
]
```

```
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

