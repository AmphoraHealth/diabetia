#!/bin/bash

if [ -d ".venv" ];
then
  rm -rf .venv
fi
  if [ -x "$(command -v python3.9)" ]; then
    # check if there is a python3.9 and retrieve the full version
    python3.9 -V > python_version.txt

  elif [ -x "$(command -v python3.10)" ]; then
    # alternatively try to use python3.10
    python3.10 -V > python_version.txt

  else
    # if no python3.9 or python3.10 is found, exit with error
    echo ">>> No python3.9 or python3.10 found"
    echo "    to make use of this code you need to install python3.9 or python3.10"
    echo "    and make sure it is available in your PATH"
    echo ""
    echo "    alternatively you can try to run the code manually script by script"
    exit 1
  fi

  # create virtual environment
  python_version=$(cat python_version.txt)
  echo ">>> '$python_version' found"
  python_version="python$(echo $python_version | cut -d' ' -f2)"
  virtualenv .venv --python=$python_version
  rm python_version.txt

  # confirm virtual environment creation
  if [ ! -d ".venv" ];
  then
    echo ">>> .venv not created"
    exit 1
  fi

  # install requirements
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r  requirements.txt
  errors=$?
  deactivate

  # exit if requirements installation failed
  if [ $errors -ne 0 ];
  then
    echo ">>> requirements installation failed"
    exit 1
  fi

# succesful exit
echo '>>> .venv created'
