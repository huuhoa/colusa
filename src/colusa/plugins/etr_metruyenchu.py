import re

from bs4 import Tag

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer


@register_extractor('//metruyenchu.com')
class MeTruyenChuExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', id='js-read__content')

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'js-left-menu'})
        self.remove_tag(self.main_content, 'div', attrs={'id': 'js-right-menu'})
        to_remove = []
        to_remove += self.main_content.select('#js-read__body div:first-child')
        to_remove += self.main_content.select('#js-read__body div:nth-child(2)')
        to_remove += self.main_content.select('#js-read__body div:nth-child(3)')
        for i in to_remove:
            i.extract()
        
        self.remove_tag(self.main_content, 'a', attrs={'class': 'truyen-title'})
        self.remove_tag(self.main_content, 'h2', attrs={})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'group_story'})
        


@register_transformer('//metruyenchu.com')
class MeTruyenChuTransformer(Transformer):
    def transform(self):
        value = super().transform()
        # cleanup hr
        value = re.sub(r'^-{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\.{4,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^_{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\*{3,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r'^\+{5,}', "'''", value, flags=re.MULTILINE)
        value = re.sub(r"^'''\n\n$", "", value, flags=re.MULTILINE)
        value = re.sub(r"^'''\n{2,}'''", "", value, flags=re.MULTILINE)
        if value.startswith(' '):
            value = value[1:]
        self.value = value
        return value

