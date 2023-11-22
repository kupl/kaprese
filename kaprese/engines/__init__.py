from kaprese.engines.cafe import register_cafe
from kaprese.engines.saver import register_saver

ENGINES = {
    "saver": register_saver,
    "cafe": register_cafe,
}
