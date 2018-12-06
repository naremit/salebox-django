from django.db import connection


def dictfetchall(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def fetchflatlist(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return [row[0] for row in cursor.fetchall()]


def fetchsinglevalue(sql):
    return fetchflatlist(sql)[0]
