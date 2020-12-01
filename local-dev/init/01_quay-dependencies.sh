#!/bin/bash 

set -e

QUAYDIR=${QUAYDIR:-"/"}

cd $QUAYDIR 

echo "[Local Dev] - Install Python Dependencies..."
alternatives --set python /usr/bin/python3 && \
    python -m pip install --no-cache-dir --upgrade setuptools pip && \
    python -m pip install --no-cache-dir -r requirements.txt --no-cache && \
    python -m pip freeze

echo "[Local Dev] - Building Front End..."
mkdir -p $QUAYDIR/static/webfonts && \
    mkdir -p $QUAYDIR/static/fonts && \
    mkdir -p $QUAYDIR/static/ldn && \
    PYTHONPATH=$QUAYPATH python -m external_libraries && \
    npm install --ignore-engines && \
    npm run build

cd -
