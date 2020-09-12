from .etr import Extractor, Transformer

"""
Dictionary of extractor
"""
__EXTRACTORS = {}

"""
Dictionary of transformer
"""
__TRANSFORMERS = {}


def register_extractor(pattern):
    def wrapper_class(arg):
        __EXTRACTORS[pattern] = arg
        return arg

    return wrapper_class


def register_transformer(pattern):
    def wrapper_class(arg):
        __TRANSFORMERS[pattern] = arg
        return arg

    return wrapper_class


def create_extractor(url_path, bs):
    for p in __EXTRACTORS.keys():
        if p in url_path:
            cls = __EXTRACTORS[p]
            return cls(bs)
    return Extractor(bs)


def create_transformer(url_path, content, root):
    config = {
        "src_url": url_path,
        "output_dir": root
    }
    for p in __TRANSFORMERS.keys():
        if p in url_path:
            cls = __TRANSFORMERS[p]
            return cls(config, content)

    return Transformer(config, content)
