from etr import Extractor


class FsblogExtractor(Extractor):
    def get_title(self):
        h1 = self.bs.find('h1', class_='entry-title')
        return h1.text

    def cleanup(self):
        self.remove_tag(self.site, 'p', attrs={
            'style': 'color: black; background: #ffffcc none repeat scroll 0% 0%; text-align: center;'
        })
        super(FsblogExtractor, self).cleanup()
