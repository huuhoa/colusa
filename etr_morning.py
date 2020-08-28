from etr import Extractor


class TheMorningPaperExtractor(Extractor):
    def get_title(self):
        header = self.bs.find('h1', class_='entry-title')
        return header.text

