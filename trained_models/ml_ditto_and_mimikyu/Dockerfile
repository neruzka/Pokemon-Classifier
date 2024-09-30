FROM python:3.12-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN python -m pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
WORKDIR ./
COPY ./classifier_model.keras ./config.ini ./lb.pickle ./loss_acc_plot.png ./ml_server.py requirements.txt ./
CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:8080", "ml_server:app"]
