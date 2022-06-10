FROM python:3.6.9
WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY start.py start.py
COPY ftp.py ftp.py
CMD ["python", "-u", "start.py"]