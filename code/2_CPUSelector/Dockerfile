FROM ubuntu:22.04


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ../requirements.txt .
COPY ../config .
COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "cpu_selector.py"]
