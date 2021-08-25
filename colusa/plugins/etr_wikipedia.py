from colusa.etr import Extractor, register_extractor


@register_extractor('.wikipedia.org/')
class WikipediaExtractor(Extractor):
    def _parse_title(self):
        title = self.bs.find('h1', id='firstHeading')
        return title.text

    def _find_main_content(self):
        return self.bs.find(id='bodyContent')
