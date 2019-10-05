from django.core.cache import cache
from saleboxdjango.models import Translation


def get_translation(lang, key, default='', translations=None):
    if translations is None:
        translations = get_translations()

    try:
        return translations[lang][key]
    except:
        if lang == 'en':
            try:
                return translations['en-US'][key]
            except:
                pass

        # fallback
        return default

def get_translations(rebuild=False):
    cache_key = 'salebox_translations'

    if rebuild:
        cache.delete(cache_key)

    # attempt to retrieve from cache
    o = cache.get(cache_key)
    if o is None:
        o = {}
        ts = Translation.objects.all()
        for t in ts:
            if t.language_code not in o:
                o[t.language_code] = {}
            o[t.language_code][t.key] = t.value
        cache.set(cache_key, o, 60 * 60 * 24 * 7)

    # return
    return o