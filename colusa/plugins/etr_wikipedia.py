from colusa.etr import Extractor, register_extractor


@register_extractor('.wikipedia.org/')
class WikipediaExtractor(Extractor):
    def get_title(self):
        title = self.bs.find('h1', id='firstHeading')
        return title.text

    def internal_init(self):
        self.site = self.bs.find(id='bodyContent')
