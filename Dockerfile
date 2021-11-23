FROM python:3.9.5
COPY . /api
WORKDIR /api
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT [ "flask" ]
CMD [ "run", "--host=0.0.0.0", "--port=8000" ]