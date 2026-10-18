# Use an official lightweight Python image
FROM python:3.13.5-slim

# Set the working directory inside the container
WORKDIR /app

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project source files into the container
COPY . .

# Expose Gradio default port
EXPOSE 7860

# Command to launch the Gradio app
CMD ["python", "app.py"]