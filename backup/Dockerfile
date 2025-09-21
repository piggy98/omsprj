# Use the official Python image as a base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Upgrade pip to the latest version to prevent errors
RUN pip install --upgrade pip

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the crawler script and the main Flask app
COPY updream_crawler.py .
COPY app.py .

# Define the command to run 