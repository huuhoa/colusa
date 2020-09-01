from etr import Extractor, Transformer, Renderer
from etr_config import JsonConfigExtractor
from etr_untools import Untools, UntoolsTransformer, UntoolsRenderer
from etr_unintendedconsequences import UnintendedConsequencesExtractor
from etr_morning import TheMorningPaperExtractor
from etr_fsblog import FsblogExtractor


def create_extractor(url_path, bs, **kwargs):
    if 'untools.co' in url_path:
        return Untools(bs)
    if 'unintendedconsequenc' in url_path:
        return UnintendedConsequencesExtractor(bs)
    if 'blog.acolyer.org' in url_path:
        return TheMorningPaperExtractor(bs)
    if 'https://fs.blog' in url_path:
        return FsblogExtractor(bs)
    if kwargs.get('experiment', False):
        return JsonConfigExtractor(kwargs.get('config', {}), bs)
    return Extractor(bs)


def create_transformer(url_path, bs, content, root):
    config = {
        "src_url": url_path,
        "output_dir": root
    }
    if 'untools.co' in url_path:
        return UntoolsTransformer(config, bs, content)
    if 'unintendedconsequenc' in url_path:
        return Transformer(config, bs, content)
    if 'blog.acolyer.org' in url_path:
        return Transformer(config, bs, content)
    return Transformer(config, bs, content)


def create_renderer(url_path):
    if 'untools.co' in url_path:
        return UntoolsRenderer()
    if 'unintendedconsequenc' in url_path:
        return Renderer()
    if 'blog.acolyer.org' in url_path:
        return Renderer()
    return Renderer()
