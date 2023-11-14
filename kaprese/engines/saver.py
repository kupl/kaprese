from kaprese.core.engine import Engine


def register_saver(overwrite: bool = False) -> None:
    saver = Engine(
        "saver",
        supported_languages=["c"],
        supported_os=["ubuntu:20.04"],
        image="ghcr.io/kupl/kaprese-engines/saver",
        basedir="",
        dockerfile="""\
FROM {{ benchmark }}
RUN export DEBIAN_FRONTEND=noninteractive \\
    && apt-get update \\
    && apt-get install -y \\
        build-essential \\
        git \\
        wget \\
        python \\
        python3 \\
        tzdata \\
        libtinfo5 \\
        libz3-dev \\
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/list/*
WORKDIR /opt
RUN wget https://koreaoffice-my.sharepoint.com/:u:/g/personal/seongjoon_korea_ac_kr/ETNyGJaRxbFEgA_IHJLyRQ0BQ9egwDuxCnpjdt4AmNHlVw\\?e\\=KGhbVN\\&download\\=1 -O saver.tar.gz \\
    && tar -xvf saver.tar.gz \\
    rm saver.tar.gz
ENV PATH=/opt/saver-1.0/infer/bin:${PATH}
""",
    )
    saver.register(overwrite=overwrite)
