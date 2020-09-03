from .etr import Extractor


class CSRutgersEduExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('div', attrs={'id': 'main'})

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'id': 'downloadmsg'})
        self.remove_tag(self.site, 'div', attrs={'id': 'headline'})
        super(CSRutgersEduExtractor, self).cleanup()
