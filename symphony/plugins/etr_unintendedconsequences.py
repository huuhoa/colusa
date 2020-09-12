from symphony.etr import Extractor
from symphony.etr_factory import register_extractor


@register_extractor('unintendedconsequenc')
class UnintendedConsequencesExtractor(Extractor):
    def get_title(self):
        return self.bs.find('h1').text

    def internal_init(self):
        self.site = self.bs.find(id='page')

    def get_content(self):
        return self.site.find(attrs={'class': 'entry-content'})
