# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

RUN apk update && \
    apk upgrade sqlite-libs && \
    apk add --no-cache \
    && rm -rf /var/cache/apk/*


# Copy dependency files
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Install the project
RUN pip install -e .

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Change ownership of app directory to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
