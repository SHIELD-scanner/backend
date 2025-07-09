# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app


# Copy dependency files
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Install the project
RUN pip install -e .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
