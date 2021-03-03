FROM python:3.9.1-alpine3.13
WORKDIR /code
ENV FLASK_APP=view.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]