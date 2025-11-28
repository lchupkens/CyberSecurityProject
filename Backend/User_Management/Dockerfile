From python:3.12-slim
Run apt-get update && apt-get install -y build-essential curl
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Backend/User_Management .
CMD ["uvicorn", "user_service_main:app", "--host", "0.0.0.0", "--port", "8001"]