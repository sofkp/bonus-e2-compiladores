FROM python:3.11-slim
WORKDIR /app
COPY lr1_parser.py lr1_web.py ./
RUN pip install flask flask-cors
EXPOSE 5000
CMD ["python", "lr1_web.py"]
