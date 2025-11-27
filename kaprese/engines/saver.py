from kaprese.core.engine import Engine


def register_saver(overwrite: bool = False) -> None:
    saver = Engine(
        "saver",
        supported_languages=["c"],
        supported_os=["ubuntu:20.04"],
        image="ghcr.io/kupl/kaprese-engines/saver",
        location="https://github.com/kupl/kaprese-engines.git#main:context/saver/starlab-benchmarks",
        build_args={
            "BENCHMARK_IMAGE": "{benchmark.image}",
        },
        exec_commands=[
            "make clean -j$(nproc) >/dev/null",
            "infer capture -- make -j$(nproc) >/dev/null",
            'infer saver --pretty --error-report report.json $([ -e api.json ] && echo \\"--resource-api-spec api.json\\") {runner.extra_args}',
            "export RETURN_CODE=$?",
            "cp -r infer-out/* {runner.mount_dir}/",
            "chown -R {runner.uid}:{runner.gid} {runner.mount_dir}",
            "exit $([ $RETURN_CODE -eq 106 ] && echo 0 || echo $RETURN_CODE)",
        ],
    )
    saver.register(overwrite=overwrite)
