FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the action's code into the container
COPY . .

# Set the entry point to the main.py script
ENTRYPOINT ["python3", "main.py"]
