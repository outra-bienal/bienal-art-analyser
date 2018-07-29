web: PYTHONPATH=$PYTHONPATH:$PWD/project gunicorn src.config.wsgi
worker: python project/manage.py rqworker default
release: python project/manage.py migrate --no-input
