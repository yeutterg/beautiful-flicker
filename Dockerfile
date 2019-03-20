# Python version: latest stable Python 3 slim
FROM python:3-slim

# Install Requirements
COPY /src /install  
RUN pip install -r /install/requirements.txt