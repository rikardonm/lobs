FROM gcc:15-trixie

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y -q \
        cmake \
        python3.13-full \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN python3.13 -m venv /venv
RUN echo "source /venv/bin/activate" >> /etc/bash.bashrc

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["bash"]
