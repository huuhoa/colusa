from colusa.etr import Extractor, register_extractor


@register_extractor('//knowledgegraph.today')
class KnowledgegraphTodayExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.body

    def get_title(self):
        p_title = self.site.find('p', class_='title')
        return p_title.text
