FROM ubuntu:22.04

# Build arguments for conditional installation
ARG ELASTICSEARCH=true
ARG NODEJS=true

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:/app/node_modules/.bin:$PATH"
ENV TURNSTILE_ENABLED="False"
ENV DJANGO_SETTINGS_MODULE=library_website.settings.docker

# Set working directory
WORKDIR /app

# Create django error log
RUN touch /var/log/django-errors.log && \
    chmod 666 /var/log/django-errors.log

# Update repos and install base dependencies
RUN rm -rf /var/lib/apt/lists/partial && \
    apt-get update -y -o Acquire::CompressionTypes::Order::=gz && \
    apt-get install -y software-properties-common

# Install Python 3.11 (upgrade from system Python 3.10)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python3.11 python3.11-distutils python3-pip python3.11-dev python3.11-venv

# Install Wagtail dependencies and dev tools
RUN apt-get install -y \
    vim git curl gettext build-essential \
    libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libllvm11 \
    redis-server postgresql-client libpq-dev \
    libxml2-dev libxslt-dev

# Setup vim with ALE for development
RUN mkdir -p /root/.vim/pack/git-plugins/start && \
    git clone --depth 1 https://github.com/dense-analysis/ale.git /root/.vim/pack/git-plugins/start/ale && \
    echo "let g:ale_linters_explicit = 1" >> /root/.vimrc && \
    echo "let g:ale_linters = { 'python': ['flake8'], 'javascript': ['eslint'] }" >> /root/.vimrc && \
    echo "let g:ale_python_flake8_options = '--ignore=D100,D101,D202,D204,D205,D400,D401,E303,E501,W503,N805,N806'" >> /root/.vimrc && \
    echo "let g:ale_fixers = { 'python': ['isort', 'autopep8', 'black'], 'javascript': ['eslint'] }" >> /root/.vimrc && \
    echo "let g:ale_python_black_options = '--skip-string-normalization'" >> /root/.vimrc && \
    echo "let g:ale_python_isort_options = '--profile black'" >> /root/.vimrc

# Conditionally install Java and Elasticsearch
RUN if [ "$ELASTICSEARCH" != "false" ]; then \
    apt-get install -y openjdk-11-jre-headless ca-certificates-java wget && \
    wget -q https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.13-amd64.deb && \
    dpkg -i elasticsearch-7.17.13-amd64.deb && \
    sed -i 's/^\(-Xm[sx]\)2g$/\1512m/g' /etc/elasticsearch/jvm.options && \
    rm elasticsearch-7.17.13-amd64.deb && \
    echo "xpack.security.enabled: false" >> /etc/elasticsearch/elasticsearch.yml; \
    fi

# Conditionally install Node.js
RUN if [ "$NODEJS" != "false" ]; then \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    npm install -g eslint@8.57.0 prettier eslint-plugin-prettier eslint-config-prettier eslint-config-airbnb install-peerdeps; \
    fi

# Install virtualenv and create Python virtual environment
RUN pip3 install virtualenv && \
    python3.11 -m venv /venv

# Setup bash environment to auto-activate venv and set working directory
RUN echo 'source /venv/bin/activate' >> /root/.bashrc && \
    echo 'cd /app' >> /root/.bashrc && \
    echo 'export PATH="/app/node_modules/.bin:$PATH"' >> /root/.bashrc && \
    echo 'export TURNSTILE_ENABLED="False"' >> /root/.bashrc

# Make static directories (in Docker volume)
RUN mkdir -p /app/static

# Clean up
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/local/lib/python3.7/test/__pycache__ 2>/dev/null || true

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy package.json for Node.js dependencies (if they exist)
COPY package*.json ./
RUN if [ "$NODEJS" != "false" ] && [ -f "package.json" ]; then \
    npm install --no-save; \
    fi

# Create news feed directory and copy test file
RUN mkdir -p /app/static/lib_news/files

# Expose port
EXPOSE 8000

# Default command
CMD ["bash"]