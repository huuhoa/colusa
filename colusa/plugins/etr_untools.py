import re

from colusa.etr import Extractor, register_extractor


@register_extractor('//untools.co')
class UntoolsExtractor(Extractor):
    def _parse_title(self):
        import re
        header = self.bs.find('div', class_=re.compile('article-module--top--'))
        title = header.find('h2').text
        return title

    def _parse_extra_metadata(self):
        import re
        header = self.bs.find('div', class_=re.compile('article-module--top--'))
        tag = header.find('span', class_=re.compile('tag-module--tag--')).text
        usage = header.find('div', class_=re.compile('article-module--when-useful--')).text

        return f'.{tag}\n****\n{usage}\n****\n\n'

    def _find_main_content(self):
        return self.bs.find(class_=re.compile('article-module--content--'))
