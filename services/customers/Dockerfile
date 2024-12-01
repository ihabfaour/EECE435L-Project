# Use Python as the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the service code
COPY ../../ /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the PYTHONPATH to make all modules discoverable
ENV PYTHONPATH=/app

# Expose the service port
EXPOSE 5001

# Run the Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
