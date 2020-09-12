from symphony.etr import Extractor
from symphony.etr_factory import register_extractor


@register_extractor('//www.preethikasireddy.com')
class PreethikasireddyExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('div', attrs={'id': 'Story'})
