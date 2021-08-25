from colusa.etr import Extractor, register_extractor


@register_extractor('//knowledgegraph.today')
class KnowledgegraphTodayExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.body

    def _parse_title(self):
        # TODO: self.main_content here might not be available, need to find other way
        p_title = self.main_content.find('p', class_='title')
        return p_title.text
