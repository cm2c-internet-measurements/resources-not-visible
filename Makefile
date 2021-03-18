# Pipeline makefile
#
#

build: requirements.txt Dockerfile
	docker build -t notvisible .

shell: build
	docker run -ti -v $$(pwd):/root/work notvisible /bin/bash
