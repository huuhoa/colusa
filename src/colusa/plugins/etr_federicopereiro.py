from colusa.etr import Extractor, register_extractor_v2


@register_extractor_v2('federicopereiro.com', '//federicopereiro.com')
class FedericopereiroExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', attrs={'class': 'container'})
