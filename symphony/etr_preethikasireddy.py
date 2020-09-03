from .etr import Extractor


class PreethikasireddyExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('div', attrs={'id': 'Story'})
