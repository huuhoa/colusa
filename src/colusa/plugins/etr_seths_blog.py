from bs4 import Tag

from colusa.etr import Extractor, register_extractor_v2
from colusa import logs

@register_extractor_v2('sethsblog', '//seths.blog')
class SethsBlogExtractor(Extractor):
    def _find_main_content(self) -> Tag:
        content = self.bs.find('div', class_='single-post')
        return content

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-footer'})
        super().cleanup()