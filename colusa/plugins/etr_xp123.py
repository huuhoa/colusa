from colusa.etr import Extractor, register_extractor


@register_extractor('//xp123.com')
class XP123Extractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('article', attrs={'class': 'post'})

    def cleanup(self):
        self.remove_tag(self.main_content, 'header', attrs={'class': 'entry-header'})
        self.remove_tag(self.main_content, 'section', attrs={'class': 'yikes-mailchimp-container'})
        self.remove_tag(self.main_content, 'footer', attrs={'class': 'entry-meta'})
