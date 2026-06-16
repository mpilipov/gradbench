FROM python:3.11-slim

# installing of basic building instruments
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    python3 \
    dos2unix \
    cmake \
    && rm -rf /var/lib/apt/lists/*
# donwloading folder nlohmann/json (for GradBench)
# put json.hpp into /usr/local/include
RUN wget -q https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp -O /usr/local/include/json.hpp
# downloading XAD into the folder /opt
WORKDIR /opt
RUN git clone https://github.com/auto-differentiation/xad.git

WORKDIR /opt/xad

RUN sed -i 's/Tape.cpp/Tape.cpp XAD\/JITCompilerTLS.cpp XAD\/JITGraphInterpreter.cpp/g' src/CMakeLists.txt
# build and install /opt/xad-install
RUN cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/opt/xad-install -DXAD_ENABLE_TESTS=OFF -DXAD_ENABLE_SAMPLES=OFF -DXAD_ENABLE_JIT=ON
RUN cmake --build build --target install

RUN cp -r /opt/xad/src/XAD/* /opt/xad-install/include/XAD/

# cd /gradbench
WORKDIR /gradbench

# copy all the folders and files of the repository
COPY . .

# building the tool (using Makefile)
# flag -C forces make to enter the folder tools/xad
RUN dos2unix tools/xad/Makefile
RUN make -C tools/xad

# entry point for GradBench
ENTRYPOINT ["python3", "python/gradbench/gradbench/cpp.py", "xad"]

LABEL org.opencontainers.image.source=https://github.com/gradbench/gradbench
