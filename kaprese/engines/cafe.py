from kaprese.core.engine import Engine


def register_cafe(overwrite: bool = False) -> None:
    cafe = Engine(
        "cafe",
        supported_languages=["ocaml"],
        supported_os=["debian:12"],
        image="ghcr.io/kupl/kaprese-engines/cafe",
        location="https://github.com/kupl/kaprese-engines.git#cafe:context/cafe/starlab-benchmarks",
        build_args={
            "BENCHMARK_IMAGE": "{benchmark.image}",
        },
        exec_commands=[
            "export ENTRY=$(cat metadata.json | jq -r .function)",
            "export PROBLEM_NAME=$(echo {benchmark.name} | cut -d'-' -f1)",
            'cafe -fix -solutions $PROBLEM_NAME -submission src.ml -testcases testcases -entry $ENTRY $([ -e test.ml ] && echo \\"-grading test.ml\\")',
            "export RETURN_CODE=$?",
            "cp -f cafe.log fixed.ml {runner.mount_dir}/",
            "chown -R {runner.uid}:{runner.gid} {runner.mount_dir}",
            "exit $RETURN_CODE",
        ],
    )
    cafe.register(overwrite=overwrite)
