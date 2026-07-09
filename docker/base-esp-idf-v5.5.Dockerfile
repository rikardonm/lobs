FROM espressif/idf:release-v5.5

ARG DEBIAN_FRONTEND=nointeractive

RUN apt-get update \
   && apt install -y -q \
   hwdata \
   libglib2.0-0 \
   libnuma1 \
   libpixman-1-0 \
   linux-tools-virtual \
   clang \
   clangd \
   cppcheck \
   udev \
   && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/local/bin/usbip usbip `ls /usr/lib/linux-tools/*/usbip | tail -n1` 20

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.13-full python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/esp/idf/export.sh > /dev/null 2>&1" >> ~/.bashrc

ENTRYPOINT [ "/opt/esp/entrypoint.sh" ]

CMD ["/bin/bash"]
