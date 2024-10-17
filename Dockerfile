# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install pipenv and set PATH
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock first (this helps with Docker caching)
COPY Pipfile Pipfile.lock /app/

# Install dependencies via Pipenv
RUN pipenv install --deploy --system

# Copy the rest of the application code into the container
COPY . /app

# Expose port if needed for webhooks (optional)
EXPOSE 8080

# Set environment variables (optional; you can also set them dynamically)
ENV TOKEN = "7561833317:AAErJUMSThTBuAfJ2PxwoBbU40tCkneWuGw"

# Command to run your bot
CMD ["pipenv", "run", "python", "bot.py"]
