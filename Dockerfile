FROM python:3.12

# Set the working directory to /app
WORKDIR /app

####################
# Install Graphite #
####################
ENV NVM_DIR=$HOME/.nvm
RUN mkdir -p $NVM_DIR
ENV NODE_VERSION=18.2.0

# Install nvm with node and npm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH=$NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN npm install -g @withgraphite/graphite-cli@stable

# Dev experience
COPY Makefile ./
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip make install

COPY . /app
RUN rm -rf cache
RUN pip install .[tests]