FROM python:latest

COPY . .
RUN apt update && \
   apt upgrade -y && \
   pip3 install -U  --default-timeout=100 pip && \
   apt install libssl-dev ffmpeg -y && \
   dpkg -i libssl*.deb && \
   pip3 install -r requirements.txt

CMD ["python3", "main.py"]
