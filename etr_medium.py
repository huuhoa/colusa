from bs4 import Tag

from etr import Extractor, Transformer


class MediumExtractor(Extractor):
    def get_title(self):
        title = self.site.find('h1')
        if title is not None:
            return title.text
        meta = self.bs.find('meta', attrs={'property': 'og:title'})
        if meta is not None:
            return meta.get('content')
        return self.bs.title.text

    def internal_init(self):
        self.site = self.bs.find('article')


class MediumTransformer(Transformer):
    def transform_tag(self, tag: Tag, indent_level=0) -> str:
        if tag.name == 'figure' and 'paragraph-image' in tag.get('class'):
            tag = tag.find('noscript')
            value = super(MediumTransformer, self).transform_tag(tag, indent_level)
            return f'{value}\n\n'
        return super(MediumTransformer, self).transform_tag(tag, indent_level)
