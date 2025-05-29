FROM hub.hamdocker.ir/library/python:3.12
WORKDIR /djangoProjectChatBot/
ADD ./requirements.txt ./
RUN pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y
RUN python manage.py collectstatic --noinput
ADD ./ ./
ENTRYPOINT ["/bin/sh", "-c" , "python manage.py migrate && celery -A djangoProjectChatBot worker --concurrency=4 --prefetch-multiplier=8 --loglevel=info & gunicorn --bind 0.0.0.0:8000 djangoProjectChatBot.wsgi"]
