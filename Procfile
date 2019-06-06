web: gunicorn src.config.wsgi --pythonpath "$PWD/project" --workers=4 --log-file -
worker: celery -A src worker -l info --workdir project
