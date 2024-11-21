FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . . 
WORKDIR /app/pr-review-agent  
ENTRYPOINT ["python3", "main.py"] 