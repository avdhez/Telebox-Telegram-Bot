# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY bot/ /app/bot/

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["python", "bot/main.py"]