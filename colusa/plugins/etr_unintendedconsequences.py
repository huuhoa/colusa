from colusa.etr import Extractor, register_extractor


@register_extractor('unintendedconsequenc')
class UnintendedConsequencesExtractor(Extractor):
    def _parse_title(self):
        return self.bs.find('h1').text

    def _find_main_content(self):
        return self.bs.find(id='page')

    def get_content(self):
        return self.main_content.find(attrs={'class': 'entry-content'})
