from colusa.etr import Extractor, register_extractor


@register_extractor('//scrumcrazy.wordpress.com')
class ScrumCrazyExtractor(Extractor):
    def __init__(self, bs):
        self._cached_author = None
        super(ScrumCrazyExtractor, self).__init__(bs)

    def _parse_author(self) -> str:
        if self._cached_author:
            return self._cached_author
        return super(ScrumCrazyExtractor, self)._parse_author()

    def _find_main_content(self):
        possible_main = super(ScrumCrazyExtractor, self)._find_main_content()
        post_info_div = possible_main.find('div', class_='postinfo')
        if post_info_div is not None:
            post_info = post_info_div.text.strip()
            import re
            m = re.search(r'by (.*)$', post_info)
            if m is not None:
                self._cached_author = m.group(1)
        entry = possible_main.find('div', class_='entry')
        if entry is not None:
            return entry
        else:
            return possible_main

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'jp-post-flair'})
        self.remove_tag(self.main_content, 'p', attrs={'class': 'postinfo'})
