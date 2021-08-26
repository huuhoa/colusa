from colusa.etr import Extractor, register_extractor


@register_extractor('fs.blog')
class FsblogExtractor(Extractor):
    def _parse_title(self):
        h1 = self.bs.find('h1', class_='entry-title')
        return h1.text

    def cleanup(self):
        self.remove_tag(self.main_content, 'p', attrs={
            'style': 'color: black; background: #ffffcc none repeat scroll 0% 0%; text-align: center;'
        })
        super(FsblogExtractor, self).cleanup()
