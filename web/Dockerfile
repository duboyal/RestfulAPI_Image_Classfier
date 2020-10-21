FROM python:3.7
RUN python3 -m pip install --upgrade pip setuptools
RUN pip3 install --upgrade pip
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "app.py" ]

#old dockerfile
# FROM python:3
# WORKDIR /usr/src/app
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD [ "python", "app.py" ]
