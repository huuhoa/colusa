from symphony.etr import Extractor
from symphony.etr_factory import register_extractor


@register_extractor('//blog.acolyer.org')
class TheMorningPaperExtractor(Extractor):
    def get_title(self):
        header = self.bs.find('h1', class_='entry-title')
        return header.text

