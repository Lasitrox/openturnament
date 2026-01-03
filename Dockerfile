FROM python:3.14
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update && apt-get install -y xdg-utils \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN tailwindcss
EXPOSE 8000
COPY . .
RUN tailwindcss

ENV RUN_TAILWIND false
# Start the app
CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
