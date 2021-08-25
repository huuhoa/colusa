from bs4 import Tag

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer


@register_extractor('//medium.com')
class MediumExtractor(Extractor):
    def _parse_title(self):
        title = self.main_content.find('h1')
        if title is not None:
            return title.text
        meta = self.bs.find('meta', attrs={'property': 'og:title'})
        if meta is not None:
            return meta.get('content')
        return self.bs.title.text

    def _find_main_content(self):
        return self.bs.find('article')


@register_transformer('//medium.com')
class MediumTransformer(Transformer):
    def transform_tag(self, tag: Tag, indent_level=0) -> str:
        if tag.name == 'figure' and 'paragraph-image' in tag.get('class'):
            tag = tag.find('noscript')
            value = super(MediumTransformer, self).transform_tag(tag, indent_level)
            return f'{value}\n\n'
        return super(MediumTransformer, self).transform_tag(tag, indent_level)
