from kaprese.core.benchmark import Benchmark
from kaprese.core.engine import Engine
from kaprese.utils.docker import build_image, image_exists, pull_image
from kaprese.utils.logging import logger


def _process_dockerfile(dockerfile: str, benchmark: Benchmark) -> str:
    dockerfile = dockerfile.replace("{{ benchmark }}", benchmark.image)
    return dockerfile


class Runner:
    def __init__(self, benchmark: Benchmark, engine: Engine):
        self.benchmark = benchmark
        self.engine = engine

    async def run(self) -> bool:
        if not self.benchmark.ready:
            self.benchmark.pull()
        if not self.benchmark.ready:
            logger.warning(f'Failed to prepare benchmark "{self.benchmark.name}"')
            return False

        runner_image_tag = f"{self.engine.image}:{self.benchmark.name}"
        if not image_exists(runner_image_tag):
            if pull_image(runner_image_tag):
                logger.info(f'Pulled runner image "{runner_image_tag}"')
            else:
                if self.engine.dockerfile is None:
                    logger.warning(
                        f'Failed to pull runner image "{runner_image_tag}" and no dockerfile provided'
                    )
                    return False
                dockerfile = _process_dockerfile(self.engine.dockerfile, self.benchmark)
                if build_image(
                    runner_image_tag, dockerfile, basedir=self.engine.basedir
                ):
                    logger.info(f'Build runner image "{runner_image_tag}"')
                else:
                    logger.warning(f'Failed to build runner image "{runner_image_tag}"')
                    return False
        return True
