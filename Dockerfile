FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the action's code into the container
COPY . .

# Debugging: List all files in the container
RUN echo "Contents of /app:" && ls -la /app && echo "Recursive listing of /app:" && ls -R /app

# Debugging: Log environment variables
RUN echo "Debugging environment variables..." \
    && echo "OPENAI_API_KEY: $OPENAI_API_KEY" \
    && echo "GITHUB_TOKEN: $GITHUB_TOKEN" \
    && echo "PR_NUMBER: $PR_NUMBER" \ 
    && echo "INPUT_OPENAI_API_KEY: $OPENAI_API_KEY" \

# Set the entry point to the main.py script
ENTRYPOINT ["python3", "/app/main.py"]
