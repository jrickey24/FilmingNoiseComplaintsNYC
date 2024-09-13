# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Create the working directory for the container
RUN mkdir /app

# Set the working directory in the container
WORKDIR /app

# Mount the current working directory as a volume
VOLUME /app
# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY src/ . 

# Specify the entry point for the container
ENTRYPOINT ["python", "main.py"]

# Default arguments for the entry point
CMD ["--default-arg1", "2023-07-01", "--default-arg2", "2023-09-30"]