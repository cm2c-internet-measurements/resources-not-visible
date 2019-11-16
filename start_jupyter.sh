#!/bin/bash

# Assumes docker installed. Will pull image if needed.
docker run -p 8888:8888 \
   -e JUPYTER_ENABLE_LAB=yes \
   -v "$PWD"/reports:/home/jovyan/reports \
   -v "$PWD"/var:/home/jovyan/var \
   jupyter/scipy-notebook:17aba6048f44 \
   start-notebook.sh --NotebookApp.token='' & 

open http://127.0.0.1:8888/
