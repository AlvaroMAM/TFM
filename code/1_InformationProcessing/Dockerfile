FROM ubuntu:22.04


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY . .

RUN mkdir temp

RUN pip3 install -r requirements.txt


EXPOSE 8586


CMD ["python3", "information_processing.py"]
