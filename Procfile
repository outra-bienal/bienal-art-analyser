web: PYTHONPATH=$PYTHONPATH:$PWD/project gunicorn src.config.wsgi
worker: PYTHONPATH=$PYTHONPATH:$PWD/project rqworker
release: python project/manage.py migrate --no-input
