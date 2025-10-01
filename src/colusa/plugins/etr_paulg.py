from bs4 import Tag

from colusa.etr import Extractor, register_extractor_v2
from colusa import logs

@register_extractor_v2('paulgraham', '//www.paulgraham.com')
class PaulGrahamExtractor(Extractor):
    def _find_main_content(self) -> Tag:
        main = self.bs.select_one('body > table > tr > td:nth-of-type(3) > table')
        content = main.select_one('tr > td > font > p')
        if content is None:
            content = main.select_one('tr > td > font')
        # logs.info(content)
        return content
