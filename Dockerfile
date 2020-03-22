FROM node:13.5-alpine AS frontend-builder
WORKDIR /frontend
RUN mkdir src
RUN mkdir public
COPY assets/src/ ./src/
COPY assets/public/ ./public/
COPY assets/jsconfig.json .
COPY assets/package.json .
COPY assets/yarn.lock .
RUN npm install
RUN npm run build

# TODO: environment variable to specify build folder
FROM python:3.8-slim
WORKDIR /root/
RUN mkdir assets/
COPY --from=frontend-builder /frontend/build/ assets/build
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir src
COPY src/ ./src/
ENV PYTHONPATH=.
CMD ["python", "src/main.py"]