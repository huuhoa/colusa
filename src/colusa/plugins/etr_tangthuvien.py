import re

from bs4 import Tag

from colusa.etr import Extractor, Transformer, register_extractor, register_transformer


@register_extractor('//truyen.tangthuvien.vn')
class TangThuVienExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', class_='content')

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'id': 'list-comment'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'bottom-box'})
        self.remove_tag(self.main_content, 'h1', attrs={'class': 'truyen-title'})
        self.remove_tag(self.main_content, 'h2', attrs={})
        self.remove_tag(self.main_content, 'h5', attrs={})
        self.remove_tag(self.main_content, 'ul', attrs={'class': 'left-control'})
        self.remove_tag(self.main_content, 'p', attrs={'class': 'text-center'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'box-adv'})

        

@register_transformer('//truyen.tangthuvien.vn')
class TangThuVienTransformer(Transformer):
    def transform(self):
        value = super(TangThuVienTransformer, self).transform()
        # cleanup hr
        value = re.sub(r'^\t', "", value, flags=re.MULTILINE)
        self.value = value
        return value

