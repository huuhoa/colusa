from .etr import Extractor


class AvikdasExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.body

    def cleanup(self):
        self.remove_tag(self.site, 'ul', attrs={'id': 'bottom-links'})
        self.remove_tag(self.site, 'h1', attrs={})
