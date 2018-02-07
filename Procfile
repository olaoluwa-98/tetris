release: python manage.py migrate && python manage.py populate_db
web: gunicorn tetris.wsgi --log-file -
