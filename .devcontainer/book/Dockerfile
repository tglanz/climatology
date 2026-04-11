FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf sudo gh less bat \
    && rm -rf /var/lib/apt/lists/* \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu \
    && chsh -s /usr/bin/zsh ubuntu

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh
ENV PATH="/opt/nvim/bin:$PATH"

COPY book/install-quarto.sh /tmp/install-quarto.sh
RUN bash /tmp/install-quarto.sh

USER ubuntu
WORKDIR /home/ubuntu

COPY common/setup-oh-my-zsh.sh /tmp/setup-oh-my-zsh.sh
RUN bash /tmp/setup-oh-my-zsh.sh \
    && echo 'export TERM=xterm-256color' >> ~/.zshrc \
    && echo 'export LS_COLORS="di=1;36:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43"' >> ~/.zshrc \
    && echo 'alias bat=batcat' >> ~/.zshrc
