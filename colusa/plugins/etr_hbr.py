import re

from bs4 import Tag

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer


@register_extractor('//hbr.org')
class HBRExtractor(Extractor):
    def _find_main_content(self):
        self.site = self.bs.find('div', class_='article-body standard-content')

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'class': 'left-rail--container'})
        self.remove_tag(self.site, 'div', attrs={'class': 'translate-message'})
        self.remove_tag(self.site, 'div', attrs={'class': 'right-rail--container'})
        self.remove_tag(self.site, 'div', attrs={'class': 'post-container'})

