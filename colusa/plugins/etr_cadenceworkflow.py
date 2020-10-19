from colusa.etr import Extractor, register_extractor


@register_extractor('https://cadenceworkflow.io')
class CadenceWorkflowExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('main')
