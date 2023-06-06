FROM python:3.8

WORKDIR /app

COPY errordetection-requirements.txt .

ENV RECORDING_ID=recording_id

RUN apt-get update
RUN apt-get install -y portaudio19-dev python3-pyaudio ffmpeg libsm6 libxext6 libgl1 libglib2.0-0 libgl1-mesa-glx libfontconfig1 libxrender1

RUN pip install --no-cache-dir -r errordetection-requirements.txt

COPY . .

CMD ["/bin/sh"]
