from pathlib import Path

from kaprese.core.eval import Eval


def eval_cafe(output_directory) -> Eval:
    eval = Eval("cafe")

    tool_dir = Path.cwd() / output_directory / "cafe"

    for benchmark_dir in tool_dir.iterdir():
        if benchmark_dir.is_dir():
            found_files = list(benchmark_dir.rglob("fixed.ml"))

            if len(found_files) == 0:
                eval.increase_total_count
            else:
                eval.increase_correct_count

    return eval
