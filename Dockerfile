# Use a base image with Python
FROM python:3.10

# Set the working directory
WORKDIR .

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Flask application code
COPY . .

EXPOSE 5000

# Set the command to run the Flask app
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]