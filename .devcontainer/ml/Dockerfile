FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf sudo gh \
    && rm -rf /var/lib/apt/lists/* \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu \
    && chsh -s /usr/bin/zsh ubuntu

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh
ENV PATH="/opt/nvim/bin:$PATH"

RUN npm install -g @anthropic-ai/claude-code \
    # Required by the nvim tree-sitter plugin
    tree-sitter-cli

USER ubuntu
WORKDIR /home/ubuntu

COPY common/setup-oh-my-zsh.sh /tmp/setup-oh-my-zsh.sh
RUN bash /tmp/setup-oh-my-zsh.sh
