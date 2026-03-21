FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    ca-certificates \
    zsh \
    fd-find \
    ripgrep \ 
    fzf \
    tmux \
    neovim \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chsh -s /bin/zsh $USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    -o /tmp/miniforge.sh \
    && bash /tmp/miniforge.sh -b -p /home/$USERNAME/miniforge3 \
    && rm /tmp/miniforge.sh

ENV PATH="/home/$USERNAME/miniforge3/bin:$PATH"

RUN conda init zsh
