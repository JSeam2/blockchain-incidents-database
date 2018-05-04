# Specify python runtime
FROM python:3.6

# Update Container
RUN apt-get update

# Set the working directory to /app 
WORKDIR /app

# Copy current directory into container at /app
ADD . /app

# Install needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME incidentDB

# Run gunicorn when the container launches
ENTRYPOINT ["python", "web.py"]
