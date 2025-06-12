FROM python:3.13-slim

RUN apt-get update && apt upgrade -y

RUN apt-get install -y \
    nano \
    freeradius \
    freeradius-ldap \
    python3-pip \
    && pip install uv

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

COPY . .