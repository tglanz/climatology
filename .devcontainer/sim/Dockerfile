FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf make sudo \
    netcdf-bin htop gh \
    && rm -rf /var/lib/apt/lists/* \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh
ENV PATH="/opt/nvim/bin:$PATH"

USER ubuntu
WORKDIR /home/ubuntu

RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    -o /tmp/miniforge.sh \
    && bash /tmp/miniforge.sh -b -p /home/ubuntu/miniforge3 \
    && rm /tmp/miniforge.sh

ENV PATH="/home/ubuntu/miniforge3/bin:$PATH"

RUN conda init zsh
