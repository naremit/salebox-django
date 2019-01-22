def salebox(request):
    try:  # used to prevent issues with wagtail preview
        return {
            'basket': request.session['basket'],
            'user': request.user
        }
    except:
        return {
            'basket': {
                'basket': {
                    'quantity': 0,
                    'loyalty': 0,
                    'price': 0,
                    'contents': {},
                },
                'wishlist': {
                    'quantity': 0,
                    'contents': [],
                }
            },
            'user': None
        }
