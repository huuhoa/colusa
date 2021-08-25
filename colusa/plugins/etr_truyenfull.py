import re

from bs4 import Tag

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer


@register_extractor('//truyenfull.vn')
class TruyenFullExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', id='chapter-big-container')

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'chapter-nav-top'})
        self.remove_tag(self.main_content, 'div', attrs={'id': 'chapter-nav-bot'})
        self.remove_tag(self.main_content, 'a', attrs={'class': 'truyen-title'})
        self.remove_tag(self.main_content, 'h2', attrs={})


@register_transformer('//truyenfull.vn')
class TruyenFullTransformer(Transformer):
    def transform_tag(self, tag: Tag, indent_level=0) -> str:
        if tag.name == 'br':
            return '\n\n'

        return super(TruyenFullTransformer, self).transform_tag(tag, indent_level)

    def transform(self):
        value = super(TruyenFullTransformer, self).transform()
        # cleanup hr
        value = re.sub(r'^-{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\.{4,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^_{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\*{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\+{5,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r"^'''\n\n$", "", value, flags=re.MULTILINE)
        value = re.sub(r"^'''\n{2,}'''", "", value, flags=re.MULTILINE)
        self.value = value
        return value

