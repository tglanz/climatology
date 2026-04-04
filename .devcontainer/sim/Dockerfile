FROM ubuntu:24.04

# Relies on the installation path in instal-nvim.sh;
# Potentially this could be a parameter to avoid this leak, but idc now
ARG NVIM_HOME=/opt/nvim
ARG MINIFORGE_HOME=/home/ubuntu/miniforge3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf make sudo build-essential gnupg unzip \
    netcdf-bin htop gh \
    && rm -rf /var/lib/apt/lists/* \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu

RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --dearmor -o /etc/apt/keyrings/charm.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" > /etc/apt/sources.list.d/charm.list \
    && apt-get update && apt-get install -y --no-install-recommends glow \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh

ENV PATH="${MINIFORGE_HOME}/bin:${NVIM_HOME}/bin:$PATH"
RUN echo "PATH=$PATH" >> /etc/environment

USER ubuntu
WORKDIR /home/ubuntu

RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    -o /tmp/miniforge.sh \
    && bash /tmp/miniforge.sh -b -p ${MINIFORGE_HOME} \
    && rm /tmp/miniforge.sh


RUN conda init zsh
