FROM ubuntu:22.04


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt


EXPOSE 8585


CMD ["python3", "web.py", "&", "python3", "update.py"]
