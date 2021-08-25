from colusa.etr import Extractor, register_extractor


@register_extractor('//scrumcrazy.wordpress.com')
class ScrumCrazyExtractor(Extractor):
    def _find_main_content(self):
        possible_main = super(ScrumCrazyExtractor, self)._find_main_content()
        post_info_div = possible_main.find('div', class_='postinfo')
        if post_info_div is not None:
            post_info = post_info_div.text.strip()
            import re
            m = re.search(r'by (.*)$', post_info)
            if m is not None:
                self.author = m.group(1)
        entry = possible_main.find('div', class_='entry')
        if entry is not None:
            return entry
        else:
            return possible_main

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'jp-post-flair'})
        self.remove_tag(self.main_content, 'p', attrs={'class': 'postinfo'})
