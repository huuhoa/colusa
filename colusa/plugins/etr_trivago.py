from colusa.etr import Extractor, register_extractor


@register_extractor('//tech.trivago.com')
class TrivagoExtractor(Extractor):
    def __init__(self, bs):
        super(TrivagoExtractor, self).__init__(bs)
        self.title = ''

    def _parse_title(self):
        return self.title

    def _parse_author(self):
        meta = self.bs.find_all('meta', attrs={'name': 'author'})
        for a in meta:
            value = a.get('content')
            if value is not None and 'trivago' not in value:
                return value

        return None

    def cleanup(self):
        self.title = self.main_content.find('header', class_='post__header').find('h1').text
        self.remove_tag(self.main_content, 'header', attrs={'class': 'post__header'})
