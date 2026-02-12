# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
# ffmpeg is required for Discord audio playback
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 4200

# Command to run the application
CMD ["python", "main.py"]
