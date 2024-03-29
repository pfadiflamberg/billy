FROM python:3.9

# required for html to pdf conversion by pdfkit
RUN apt-get update && apt-get install locales -y \
    &&  sed -i -e 's/# de_CH.UTF-8 UTF-8/de_CH.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

WORKDIR /usr/src/app
COPY requirements.txt ./
# script to install wkhtmltopdf for pdfkit
COPY before-script.sh ./
RUN pip install --no-cache-dir -r requirements.txt && sh before-script.sh

COPY . .

CMD [ "python", "./billy/app.py" ]