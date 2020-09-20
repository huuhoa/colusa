from symphony.etr import Extractor, register_extractor


@register_extractor('engineering.atspotify.com')
class EngineeringSpotifyExtractor(Extractor):
    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'class': 'share-block'})
        super(EngineeringSpotifyExtractor, self).cleanup()
