from colusa.etr import Extractor, register_extractor


@register_extractor('avikdas.com')
class AvikdasExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.body

    def cleanup(self):
        self.remove_tag(self.main_content, 'ul', attrs={'id': 'bottom-links'})
        self.remove_tag(self.main_content, 'h1', attrs={})
