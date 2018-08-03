web: gunicorn src.config.wsgi --pythonpath "$PWD/project" --workers=4 --log-file -
worker: python project/manage.py rqworker default
