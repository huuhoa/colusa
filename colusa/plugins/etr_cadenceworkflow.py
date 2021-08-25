from colusa.etr import Extractor, register_extractor


@register_extractor('https://cadenceworkflow.io')
class CadenceWorkflowExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('main')
