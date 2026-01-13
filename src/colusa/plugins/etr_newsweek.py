from bs4 import Tag

from colusa.etr import Extractor, register_extractor_v2
from colusa import logs

@register_extractor_v2('newsweek', '//www.newsweek.com')
class NewsWeekExtractor(Extractor):
    def _find_main_content(self) -> Tag:
        content = self.bs.find('main')
        # structure is: <main> main
        # <article> content
        #  <article>  postContent...
        content = content.find('article') if content else None
        content = content.find('article') if content else None
        return content

    def cleanup(self):
        super().cleanup()