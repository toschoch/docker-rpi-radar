FROM balenalib/raspberrypi3-python:3.7-build as builder

RUN apt-get update \
    && apt-get install -y build-essential libatlas3-base\
                          libjemalloc-dev libboost-dev \
                          libboost-filesystem-dev \
                          libboost-system-dev \
                          libboost-regex-dev \
                          python3-dev \
                          autoconf \
                          flex \
                          bison \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip wheel && \
    pip wheel numpy pyzmq --index-url https://www.piwheels.org/simple --wheel-dir \wheels
RUN pip wheel pyarrow --wheel-dir \wheels

FROM balenalib/raspberrypi3-python:3.7-run as runner

RUN install_packages libatlas3-base libzmq

COPY --from=builder /wheels /wheels
COPY requirements.txt /

RUN pip install --upgrade pip wheel && \
    pip install -r requirements.txt --wheel-dir \wheels

COPY *.py ./

CMD ["python3", "process.py"]
