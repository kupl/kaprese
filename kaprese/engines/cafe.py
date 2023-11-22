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
            "set -o pipefail",
            "export PROBLEM_NAME=$(echo {benchmark.name} | cut -d'-' -f1)",
            "/opt/LearnML/engine/main.native -fix -solutions /opt/LearnML/benchmarks/C/${{PROBLEM_NAME}} "
            "-submission src.ml -testcases testcases "
            '$([-e test.ml ] && \\"-entry grading -grading test.ml\\" || echo \\"-entry ${{PROBLEM_NAME}}\\") '
            "| tee {runner.mount_dir}/cafe.log",
            "export RETURN_CODE=$?",
            "chown -R {runner.uid}:{runner.gid} {runner.mount_dir}",
            "exit $RETURN_CODE",
        ],
    )
    cafe.register(overwrite=overwrite)
