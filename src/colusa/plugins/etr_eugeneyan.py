from colusa.etr import Extractor, register_extractor


@register_extractor('//eugeneyan.com')
class EugeneyanExtractor(Extractor):
    def _parse_title(self):
        title = self.bs.find('h1', class_='title')
        return title.text

    def _find_main_content(self):
        return self.bs.find('div', class_='notebody')
