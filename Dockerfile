FROM python:3.12-bookworm as builder
WORKDIR /app

# Install build utilities and python requirements
ENV RYE_HOME="/opt/rye"
ENV PATH="$RYE_HOME/shims:$PATH"
RUN curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" RYE_TOOLCHAIN="/usr/local/bin/python" RYE_VERSION=0.26.0 bash
RUN rye config --set-bool behavior.use-uv=true
RUN rye config --set-bool behavior.global-python=true
RUN rye config --set default.dependency-operator="~="

COPY Makefile ./
COPY pyproject.toml ./
RUN make install

COPY . /app
RUN python memorymarker/docker.py