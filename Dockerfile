FROM python:3.12-slim

RUN useradd --create-home --uid 10001 --shell /bin/sh sandbox

USER sandbox
WORKDIR /workspace
