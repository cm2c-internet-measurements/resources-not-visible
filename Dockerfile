FROM ubuntu
COPY requirements.txt /root
RUN apt-get update && apt-get -y install build-essential autoconf libtool libtool-bin git python3 python3-pip wget vim-tiny sqlite3
RUN pip3 install -r /root/requirements.txt
