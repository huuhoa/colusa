from colusa.etr import Extractor, register_extractor


@register_extractor('//blog.acolyer.org')
class TheMorningPaperExtractor(Extractor):
    def _parse_title(self):
        header = self.bs.find('h1', class_='entry-title')
        return header.text

