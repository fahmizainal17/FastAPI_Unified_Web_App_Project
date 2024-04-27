ARG LAMBDA_TASK_ROOT="/var/task"

FROM python:3.9-slim-bullseye

RUN echo "### --- Ubuntu dependencies --- ###"
RUN apt-get update && \
    apt-get install -y \
    g++ \
    cmake \
    unzip \
    curl \
    poppler-utils 

# DIRECTORY
RUN echo "### --- Directory setup -- ###"
ARG LAMBDA_TASK_ROOT
RUN mkdir -p ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}
RUN mkdir ./app
COPY ./app ${LAMBDA_TASK_ROOT}/app

# PACKAGES
WORKDIR ${LAMBDA_TASK_ROOT}/app
COPY ./app/requirements.txt ${LAMBDA_TASK_ROOT}/app
RUN pip install --no-cache-dir -r requirements.txt 

RUN echo "### --- Install spacy -- ###"
RUN python3 -m spacy download en_core_web_md
ENV FASTAPI_APP=main.py
WORKDIR ${LAMBDA_TASK_ROOT}

CMD ["uvicorn", "app.main:app", "--reload", \
    "--host", "0.0.0.0" ,\
    "--port", "80"]
EXPOSE 80