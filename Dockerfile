# Python version: latest stable Python 3 slim
FROM python:3-slim

# Set the working directory
COPY /src /src
WORKDIR /src

# Add the Jupyter directory
COPY /examples /examples

# Add the input and output directories
COPY /CSVs /CSVs
COPY /out /out

# Install requirements
RUN pip install -r requirements.txt