# Use the official Python image from the Docker Hub as a base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code into the container
COPY . /app/

# Expose the port the FastAPI app will run on (default is 8000)
EXPOSE 8000

# Define the command to run your FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
