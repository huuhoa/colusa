from colusa.etr import Extractor, register_extractor


@register_extractor('//www.preethikasireddy.com')
class PreethikasireddyExtractor(Extractor):
    def _find_main_content(self):
        self.site = self.bs.find('div', attrs={'id': 'Story'})
