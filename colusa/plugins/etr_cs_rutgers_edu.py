from colusa.etr import Extractor, register_extractor


@register_extractor('www.cs.rutgers.edu/~pxk/')
class CSRutgersEduExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', attrs={'id': 'main'})

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'downloadmsg'})
        self.remove_tag(self.main_content, 'div', attrs={'id': 'headline'})
        super(CSRutgersEduExtractor, self).cleanup()
