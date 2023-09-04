from colusa.etr import Extractor, register_extractor


@register_extractor('//lethain.com')
class LethainExtractor(Extractor):
    def __init__(self, bs):
        super(LethainExtractor, self).__init__(bs)

    def cleanup(self):
        self.remove_tag(self.main_content, 'header', None)
