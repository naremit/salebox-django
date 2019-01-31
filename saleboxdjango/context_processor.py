def salebox(request):
    return {
        'basket': request.session['basket'],
        'user': request.user
    }
