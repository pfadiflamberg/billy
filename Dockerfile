FROM python:3.9

# required for html to pdf conversion by pdfkit
RUN apt-get install wkhtmltopdf

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./billy/app.py" ]