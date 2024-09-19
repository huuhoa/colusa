from colusa.etr import Extractor, Transformer, register_extractor, register_transformer
from colusa.asciidoc_visitor import AsciidocVisitor
from bs4 import Tag
import re

@register_extractor('//newsletter.pragmaticengineer.com')
class PragmaticEngineerExtractor(Extractor):
    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'subscribe-widget'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'share-dialog'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'subscribe-footer'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'publication-footer'})
        self.remove_tag(self.main_content, 'a', attrs={'class': 'post-ufi-button'})
        self.remove_tag(self.main_content, 'a', attrs={'class': 'tweet-link-bottom'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'tweet-header'})
        

        super(PragmaticEngineerExtractor, self).cleanup()


class PEAsciidocVisitor(AsciidocVisitor):
    visit_tag_source = AsciidocVisitor.visit_tag_fall_through
    # visit_tag_div = AsciidocVisitor.visit_tag_fall_through

    def visit_tag_a(self, node, *args, **kwargs):
        href = node.get('href', '')
        # kwargs['href'] = href
        text = self.generic_visit(node, *args, **kwargs)
        # del kwargs['href']
        if not text:
            return ''
        m = re.match(r'https?://', href)
        if m is None:
            return text
        # special handling for tweet
        class_ = node.get('class', [])
        if 'tweet-link-top' in class_:
            return text

        if len(node.contents) == 1:
            child = node.contents[0]
            if type(child) is Tag and child.name == 'img':
                # anchor around image, should ignore the anchor
                return text

        if kwargs.get('figure', False):
            # parent is figure, no need to create a link
            return text

        return f'link:{href}[{text}]'
    
    def visit_tag_figure(self, node, *args, **kwargs):
        kwargs['figure'] = True
        text = super().visit_tag_figure(node, *args, **kwargs)
        del kwargs['figure']
        return text

@register_transformer('//newsletter.pragmaticengineer.com')
class PragmaticEngineerTransformer(Transformer):
    def create_visitor(self):
        return PEAsciidocVisitor()
