from symphony.etr import Extractor, register_extractor


@register_extractor('avikdas.com')
class AvikdasExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.body

    def cleanup(self):
        self.remove_tag(self.site, 'ul', attrs={'id': 'bottom-links'})
        self.remove_tag(self.site, 'h1', attrs={})
