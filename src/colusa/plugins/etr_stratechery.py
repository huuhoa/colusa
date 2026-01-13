from bs4 import Tag

from colusa.etr import Extractor, register_extractor_v2
from colusa import logs

@register_extractor_v2('stratechery', '//stratechery.com')
class StratecheryExtractor(Extractor):
    def _find_main_content(self) -> Tag:
        content = self.bs.find('main')
        return content

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'sharedaddy'})
        self.remove_tag(self.main_content, 'nav', attrs={})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-navigation-link-previous'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-navigation-link-next'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'stratechery-sidebar'})
        super().cleanup()