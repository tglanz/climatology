FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh
ENV PATH="/opt/nvim/bin:$PATH"

RUN npm install -g @anthropic-ai/claude-code

USER ubuntu
WORKDIR /home/ubuntu
