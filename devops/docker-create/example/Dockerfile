# This Dockerfile sets up a Python server environment (it's an example for what I could do with Bible Insight Server).
# Read more: https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/

FROM python:3.13
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY src ./src
EXPOSE 8080

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]