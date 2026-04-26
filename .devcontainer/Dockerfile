FROM ubuntu:24.04

ARG NVIM_HOME=/opt/nvim
ARG MINIFORGE_HOME=/home/ubuntu/miniforge3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git wget ca-certificates zsh tmux ripgrep fd-find fzf make sudo build-essential gnupg unzip less bat \
    netcdf-bin htop gh \
    && rm -rf /var/lib/apt/lists/* \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu \
    && chsh -s /usr/bin/zsh ubuntu

RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --dearmor -o /etc/apt/keyrings/charm.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" > /etc/apt/sources.list.d/charm.list \
    && apt-get update && apt-get install -y --no-install-recommends glow \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

RUN npm install -g @anthropic-ai/claude-code \
    # Required by the nvim tree-sitter plugin
    tree-sitter-cli

COPY common/install-nvim.sh /tmp/install-nvim.sh
RUN bash /tmp/install-nvim.sh

COPY common/install-quarto.sh /tmp/install-quarto.sh
RUN bash /tmp/install-quarto.sh

COPY common/install-go.sh /tmp/install-go.sh
RUN bash /tmp/install-go.sh

ENV PATH="${MINIFORGE_HOME}/bin:${NVIM_HOME}/bin:/opt/go/bin:$PATH"
RUN echo "PATH=$PATH" >> /etc/environment

USER ubuntu
WORKDIR /home/ubuntu

COPY common/setup-oh-my-zsh.sh /tmp/setup-oh-my-zsh.sh
RUN bash /tmp/setup-oh-my-zsh.sh \
    && echo 'export TERM=xterm-256color' >> ~/.zshrc \
    && echo 'export LS_COLORS="di=1;36:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43"' >> ~/.zshrc \
    && echo 'alias bat=batcat' >> ~/.zshrc

RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    -o /tmp/miniforge.sh \
    && bash /tmp/miniforge.sh -b -p ${MINIFORGE_HOME} \
    && rm /tmp/miniforge.sh

ENTRYPOINT ["/usr/bin/zsh"]
