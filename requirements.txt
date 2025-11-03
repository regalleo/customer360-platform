FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENV FLASK_ENV=production
ENV MONGO_URI=mongodb://localhost:27017/
CMD ["python", "dashboard/app.py"]
