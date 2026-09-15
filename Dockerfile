FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        cargo \
        cmake \
        git \
        golang-go \
        jq \
        nodejs \
        npm \
        default-jdk-headless \
        perl \
        php-cli \
        ruby \
        rustc \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 --shell /bin/sh sandbox

USER sandbox
WORKDIR /workspace
