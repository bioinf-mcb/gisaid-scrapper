FROM fedora:31

RUN dnf update -y && dnf install python3 python3-pip firefox -y
COPY requirements.txt /home
RUN pip3 install -r /home/requirements.txt
COPY geckodriver /usr/bin/
RUN chown root:root /usr/bin/geckodriver && chmod +x /usr/bin/geckodriver
WORKDIR /home
CMD ["python3", "scrap.py", "--headless"]
