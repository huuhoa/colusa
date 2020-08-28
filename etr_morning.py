from etr import Extractor


class TheMorningPaperExtractor(Extractor):
    def get_title(self):
        header = self.bs.find('h1', class_='entry-title')
        return header.text

    def cleanup(self):
        self.site = self.bs.find('div', class_='entry-content')
        super(TheMorningPaperExtractor, self).cleanup()

