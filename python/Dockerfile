FROM python:3.11-slim

WORKDIR /app

# Copy project
COPY . .

# Install broadcastio (editable or normal)
RUN pip install --upgrade pip \
    && pip install .

CMD ["python", "run_test.py"]
