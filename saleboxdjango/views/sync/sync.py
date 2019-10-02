from django import forms
from django.http import JSONResponse



def SaleboxSyncView(request):
    status = True

    # check the incoming ip address
    #
    #

    # check the form parameters
    if status:
        pass
        #
        #

    # reset LastUpdate
    if status:
        pass
        #
        #

    return JSONResponse({
        'status': 'OK' is status else 'Fail'
    })