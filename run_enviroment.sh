#!/bin/bash

if [ -d ".venv" ];
then
  rm -rf .venv
fi
  virtualenv .venv --python=python3.9.8
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r  requirements.txt
  deactivate
echo '>>> .venv created'

