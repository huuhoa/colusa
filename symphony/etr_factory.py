from .etr import Extractor, Transformer, Render
from .etr_avikdas import AvikdasExtractor
from .etr_cs_rutgers_edu import CSRutgersEduExtractor
from .etr_engineering_sportify import EngineeringSpotifyExtractor
from .etr_fsblog import FsblogExtractor
from .etr_increment import IncrementDotComExtractor
from .etr_medium import MediumExtractor, MediumTransformer
from .etr_morning import TheMorningPaperExtractor
from .etr_preethikasireddy import PreethikasireddyExtractor
from .etr_slack_engineering import SlackEngineeringExtractor
from .etr_truyenfull import TruyenFullExtractor, TruyenFullTransformer
from .etr_unintendedconsequences import UnintendedConsequencesExtractor
from .etr_untools import UntoolsExtractor


def create_extractor(url_path, bs):
    if 'untools.co' in url_path:
        return UntoolsExtractor(bs)
    if 'unintendedconsequenc' in url_path:
        return UnintendedConsequencesExtractor(bs)
    if 'blog.acolyer.org' in url_path:
        return TheMorningPaperExtractor(bs)
    if '://fs.blog' in url_path:
        return FsblogExtractor(bs)
    if '://increment.com' in url_path:
        return IncrementDotComExtractor(bs)
    if '//slack.engineering' in url_path:
        return SlackEngineeringExtractor(bs)
    if '//medium.com' in url_path:
        return MediumExtractor(bs)
    if '//www.cs.rutgers.edu/~pxk/' in url_path:
        return CSRutgersEduExtractor(bs)
    if '//www.preethikasireddy.com' in url_path:
        return PreethikasireddyExtractor(bs)
    if '//engineering.atspotify.com' in url_path:
        return EngineeringSpotifyExtractor(bs)
    if '//truyenfull.vn' in url_path:
        return TruyenFullExtractor(bs)
    if '//avikdas.com' in url_path:
        return AvikdasExtractor(bs)
    return Extractor(bs)


def create_transformer(url_path, content, root):
    config = {
        "src_url": url_path,
        "output_dir": root
    }
    if 'untools.co' in url_path:
        return Transformer(config, content)
    if 'unintendedconsequenc' in url_path:
        return Transformer(config, content)
    if 'blog.acolyer.org' in url_path:
        return Transformer(config, content)
    if '//medium.com' in url_path:
        return MediumTransformer(config, content)
    if '//truyenfull.vn' in url_path:
        return TruyenFullTransformer(config, content)

    return Transformer(config, content)
