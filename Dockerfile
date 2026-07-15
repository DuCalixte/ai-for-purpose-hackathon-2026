#  --- Build Stage ---
FROM python:3.12-slim AS builder

ENV APP_HOME=/home/app

WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apt-get -qq update && apt-get install --no-install-recommends -y \
    build-essential \
    gcc \
    curl \
    git \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    ca-certificates \
    libyaml-dev \
    shared-mime-info \
    && apt-get -qq clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install pyenv
ENV VIRTUALENV=nyc_hospital_sparcs_agent
ENV PYENV_ROOT=/root/.pyenv
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
ENV PATH="${PYENV_ROOT}/plugins/pyenv-virtualenv/shims:${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
ENV PYENV_PATH="${PYENV_ROOT}/versions/${VIRTUALENV}/bin"
RUN curl https://pyenv.run | bash

# RUN which pyenv

# Set your required Python version
ARG PYTHON_VERSION=3.12.13

RUN pyenv install $PYTHON_VERSION
RUN pyenv global $PYTHON_VERSION
RUN pyenv local $PYTHON_VERSION

ENV PATH="${PYENV_PATH}:${PATH}"

COPY requirements.txt .
COPY ./app ${APP_HOME}/app

RUN which pyenv

RUN pyenv virtualenv 3.12.13 $VIRTUALENV

RUN pip install --no-cache-dir -r requirements.txt

# PORT Binding with uvicorn
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
