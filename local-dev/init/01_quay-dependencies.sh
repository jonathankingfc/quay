#!/bin/bash 

set -e

QUAYDIR=${QUAYDIR:-"/"}

cd $QUAYDIR 

echo "[Local Dev] - Building Front End..."
mkdir -p $QUAYDIR/static/webfonts && \
    mkdir -p $QUAYDIR/static/fonts && \
    mkdir -p $QUAYDIR/static/ldn && \
    PYTHONPATH=$QUAYPATH python -m external_libraries && \
    npm install --ignore-engines && \
    npm run build

cd -
