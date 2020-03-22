FROM python:3.7

COPY requirements.txt /home
RUN pip install -r /home/requirements.txt
COPY geckodriver /usr/bin/
RUN chown root:root /usr/bin/geckodriver && chmod +x /usr/bin/geckodriver
WORKDIR /home
CMD ["python", "scrap.py", "--headless"]
