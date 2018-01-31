release: python manage.py migrate && python manage.py collectstatic
web: gunicorn tetris.wsgi --log-file -