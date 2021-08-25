from colusa.etr import Extractor, register_extractor


@register_extractor('//xp123.com')
class XP123Extractor(Extractor):
    def __init__(self, bs):
        self.author = None
        self.published = None
        super(XP123Extractor, self).__init__(bs)

    def _find_main_content(self):
        self.site = self.bs.find('article', attrs={'class': 'post'})

    def cleanup(self):
        self.remove_tag(self.site, 'header', attrs={'class': 'entry-header'})
        self.remove_tag(self.site, 'section', attrs={'class': 'yikes-mailchimp-container'})
        self.remove_tag(self.site, 'footer', attrs={'class': 'entry-meta'})

    def _parse_author(self):
        return self.author if self.author else super(XP123Extractor, self)._parse_author()

    def _parse_published(self):
        return self.published if self.published else super(XP123Extractor, self)._parse_published()


