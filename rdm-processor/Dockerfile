FROM python:3.7-slim as builder

RUN apt-get update \
    && apt-get install -y build-essential libatlas3-base\
                          libjemalloc-dev libboost-dev \
                          libboost-filesystem-dev \
                          libboost-system-dev \
                          libboost-regex-dev \
                          python3-dev \
                          autoconf \
                          flex \
                          git \
                          bison \
                          cmake


RUN pip install --upgrade pip wheel && \
    pip wheel numpy pyzmq pytz Cython --extra-index-url https://www.piwheels.org/simple --wheel-dir \wheels &&\
    pip install --no-index --find-links /wheels numpy pyzmq Cython

ARG ARROW_BUILD_TYPE=release
ENV ARROW_HOME=/usr/local \
    PARQUET_HOME=/usr/local

RUN git clone https://github.com/apache/arrow.git && cd arrow && git checkout apache-arrow-3.0.0 && cd ..
RUN mkdir arrow/cpp/build && \
    cd arrow/cpp/build && \

    cmake -DCMAKE_BUILD_TYPE=$ARROW_BUILD_TYPE \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
      -DARROW_WITH_BZ2=ON \
      -DARROW_WITH_ZLIB=ON \
      -DARROW_WITH_ZSTD=ON \
      -DARROW_WITH_LZ4=ON \
      -DARROW_WITH_SNAPPY=ON \
      -DARROW_WITH_BROTLI=ON \
      -DARROW_PARQUET=ON \
      -DARROW_PYTHON=ON \
      -DARROW_IPC=ON \
      -DARROW_BUILD_TESTS=OFF \
       .. && \
    make -j4 && \
    make install &&\
    cd ..


RUN cd arrow/python && \
    export PYARROW_WITH_PARQUET=1 && \
    pip install -r requirements-build.txt && \
    python setup.py build_ext --build-type=$ARROW_BUILD_TYPE --with-parquet \
       --bundle-arrow-cpp bdist_wheel
RUN cp /arrow/python/dist/*.whl /wheels

FROM python:3.7-slim as runner

RUN apt-get update && apt-get -y install libatlas3-base \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt /

RUN pip install --upgrade pip wheel && \
    pip install -r requirements.txt --no-index --find-links \wheels && \
    rm -rf \wheels

COPY *.py ./

CMD ["python3", "process.py"]
