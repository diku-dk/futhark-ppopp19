# From https://github.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#is-opencl-supported
FROM nvidia/opencl:devel-ubuntu18.04

# We keep it simple and do everything as root.  First go to our home directory.
WORKDIR /root

# Then install the necessary dependencies.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update \
    && apt -y install binutils build-essential nvidia-cuda-toolkit sqlite3 libsqlite3-dev libtinfo-dev python-pip git curl wget bc libffi-dev libgmp-dev zlib1g-dev texlive texlive-latex-extra texlive-fonts-recommended dvipng locales \
    && rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN pip install opentuner matplotlib
RUN curl -sSL https://get.haskellstack.org/ | sh

# Finally, fetch the repository.
RUN git clone --recursive https://github.com/diku-dk/futhark-ppopp19.git

# Run bash inside the fetched repository when the container is opened.  At this
# point the user just needs to type 'make'.
WORKDIR /root/futhark-ppopp19
CMD ["bash"]
