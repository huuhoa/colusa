from etr import Extractor


class FsblogExtractor(Extractor):
    def get_title(self):
        h1 = self.bs.find('h1', class_='entry-title')
        return h1.text
