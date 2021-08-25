from colusa.etr import Extractor, register_extractor


@register_extractor('//scrumcrazy.wordpress.com')
class ScrumCrazyExtractor(Extractor):
    def __init__(self, bs):
        self.author = None
        super(ScrumCrazyExtractor, self).__init__(bs)

    def _parse_author(self):
        if self.author:
            return self.author
        else:
            return super(ScrumCrazyExtractor, self)._parse_author()

    def _find_main_content(self):
        super(ScrumCrazyExtractor, self)._find_main_content()
        post_info_div = self.main_content.find('div', class_='postinfo')
        if post_info_div is not None:
            post_info = post_info_div.text.strip()
            import re
            m = re.search(r'by (.*)$', post_info)
            if m is not None:
                self.author = m.group(1)
        entry = self.main_content.find('div', class_='entry')
        if entry is not None:
            self.site = entry

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'id': 'jp-post-flair'})
        self.remove_tag(self.site, 'p', attrs={'class': 'postinfo'})
