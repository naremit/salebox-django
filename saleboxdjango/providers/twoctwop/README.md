This code currently works with 2C2P's Redirect API service only.
See: https://developer.2c2p.com/docs/how-it-works

---

The following requirements needs to be installed:
pip install python-2c2p

---

For the front-end callback to work, you need to set the following in settings.py:
SESSION_COOKIE_SAMESITE = None

This is because:
 - the callback from 2c2p is a POST
 - so the cookie is ignored
 - django creates a new session
 - meaing the user is logged out on return to the website.
The default value for CSRF_COOKIE_SAMESITE remains as 'Lax' so no damaging data is leaked.
