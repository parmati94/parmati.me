FROM debian:bookworm-slim

# git+ssh to pull the resume repo; fontconfig + Times New Roman (ms core fonts,
# contrib repo, EULA preseeded) so the PDF matches the Overleaf original.
RUN echo 'deb http://deb.debian.org/debian bookworm main contrib' > /etc/apt/sources.list.d/contrib.list \
    && apt-get update \
    && echo 'ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true' | debconf-set-selections \
    && apt-get install -y --no-install-recommends \
       git openssh-client python3 ca-certificates curl fontconfig ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

# tectonic — single-binary TeX engine (XeTeX-based)
RUN curl -sfL "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz" \
    | tar xz -C /usr/local/bin tectonic && tectonic --version

WORKDIR /app
COPY parser.py sync.py ./

# TeX package cache persists in the state volume across runs.
ENV XDG_CACHE_HOME=/state/cache

CMD ["python3", "sync.py"]
