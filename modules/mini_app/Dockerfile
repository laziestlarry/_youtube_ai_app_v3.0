FROM python:3.10-slim

WORKDIR /usr/src/app/youtube-income-commander-mini

COPY ./requirements.txt /usr/src/app/youtube-income-commander-mini/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /usr/src/app/youtube-income-commander-mini/app
# COPY ./.env /usr/src/app/youtube-income-commander-mini/.env

EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]