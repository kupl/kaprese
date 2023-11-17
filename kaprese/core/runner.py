from kaprese.core.benchmark import Benchmark
from kaprese.core.engine import Engine
from kaprese.utils.docker import build_image, delete_image, image_exists, pull_image
from kaprese.utils.logging import logger


class Runner:
    def __init__(self, benchmark: Benchmark, engine: Engine):
        self.benchmark = benchmark
        self.engine = engine

    def run(self, *, delete_runner: bool = False) -> bool:
        if not self.benchmark.ready:
            logger.info('Trying to prepare benchmark "%s"', self.benchmark.name)
            self.benchmark.prepare()
        if not self.benchmark.ready:
            logger.error('Failed to prepare benchmark "%s"', self.benchmark.name)
            return False

        runner_image_tag = f"{self.engine.image}:{self.benchmark.name}"
        if not image_exists(runner_image_tag):
            logger.info('Trying to pull or build engine image "%s"', self.engine.image)
            if pull_image(runner_image_tag):
                logger.info('Pulled runner image "%s"', runner_image_tag)
            else:
                logger.info('No prebuilt runner image "%s"', runner_image_tag)
                if self.engine.location is None:
                    logger.error(
                        'Failed to pull runner image "%s": no engine location provided',
                        runner_image_tag,
                    )

                    return False
                build_args = self._process_build_args(self.engine.build_args)
                if build_image(runner_image_tag, self.engine.location, build_args):
                    logger.info('Built runner image "%s"', runner_image_tag)
                else:
                    logger.warning(
                        'Failed to build runner image "%s": maybe wrong location? (current=%s)',
                        runner_image_tag,
                        self.engine.location,
                    )
                    return False

        logger.info(
            'Running benchmark "%s" with engine "%s"',
            self.benchmark.name,
            self.engine.name,
        )

        if delete_runner:
            logger.info('Deleting runner image "%s"', runner_image_tag)
            delete_image(runner_image_tag)

        return True

    def _process_build_args(self, build_args: dict[str, str]) -> dict[str, str]:
        return {k: v.format(benchmark=self.benchmark) for k, v in build_args.items()}
