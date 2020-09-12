import re

from symphony.etr import Extractor, register_extractor


@register_extractor('//untools.co')
class UntoolsExtractor(Extractor):
    def get_title(self):
        import re
        header = self.bs.find('div', class_=re.compile('article-module--top--'))
        title = header.find('h2').text
        return title

    def get_metadata(self):
        import re
        header = self.bs.find('div', class_=re.compile('article-module--top--'))
        tag = header.find('span', class_=re.compile('tag-module--tag--')).text
        usage = header.find('div', class_=re.compile('article-module--when-useful--')).text

        return f'.{tag}\n****\n{usage}\n****\n\n'

    def internal_init(self):
        self.site = self.bs.find(class_=re.compile('article-module--content--'))
