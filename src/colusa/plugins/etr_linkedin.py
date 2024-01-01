from colusa.etr import Extractor, register_extractor


@register_extractor('//www.linkedin.com')
class LinkedInExtractor(Extractor):
    def cleanup(self):
        self.remove_tag(self.main_content, 'header', attrs={})
        super(LinkedInExtractor, self).cleanup()
