salebox-django
===================

Connect a standalone Django ecommerce website to a GetSalebox.com backoffice.


### New: Get the latest Maxmind GeoLite2 City database

`cd` to your `/var/www/[my project]` folder, then:

    wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
    tar xvzf GeoLite2-City.tar.gz
    rm GeoLite2-City.tar.gz
    rm -rf geo
    mv GeoLite2-City_* geo
