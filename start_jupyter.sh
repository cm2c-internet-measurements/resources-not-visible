# Assumes docker installed. Will pull image if needed.
docker run -p 8888:8888 -v "$PWD"/reports:/home/jovyan/var jupyter/scipy-notebook:17aba6048f44 &

open http://127.0.0.1:8888/
