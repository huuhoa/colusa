from colusa.etr import Extractor, register_extractor


@register_extractor('.techtarget.com/')
class TechTargetExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('section', id='content-body')

    def cleanup(self):
        super(TechTargetExtractor, self).cleanup()
