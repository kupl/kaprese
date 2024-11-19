from kaprese.utils.const import OUTPUT_DIRECTORY
from kaprese.core.eval import Eval

from pathlib import Path


def eval_cafe() -> Eval:
    eval = Eval("cafe")

    tool_dir = Path.cwd() / OUTPUT_DIRECTORY / "cafe"

    for benchmark_dir in tool_dir.iterdir():
        if benchmark_dir.is_dir():
            found_files = list(benchmark_dir.rglob("fixed.ml"))

            if len(found_files) == 0:
                eval.increase_total_count
            else:
                eval.increase_correct_count

    return eval
