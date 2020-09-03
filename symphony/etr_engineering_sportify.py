from .etr import Extractor


class EngineeringSpotifyExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('main', attrs={'id': 'main'})

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'class': 'share-block'})
        self.remove_tag(self.site, 'aside', attrs={'class': 'asidebar'})
        super(EngineeringSpotifyExtractor, self).cleanup()
