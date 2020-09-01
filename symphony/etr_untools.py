import re

from symphony.etr import Renderer, Transformer, Extractor


class UntoolsRenderer(Renderer):
    def render_tag_div(self, file_out, div):
        file_out.write(div.text)
        file_out.write('\n\n')


class UntoolsTransformer(Transformer):
    def transform_h2(self):
        for a in self.site.find_all('h2'):
            text = a.text
            repl = f'=== {text}\n\n'
            p = self.doc.new_tag('p')
            p.string = repl
            a.replace_with(p)

    def transform_h3(self):
        for a in self.site.find_all('h3'):
            text = a.text
            repl = f'==== {text}\n\n'
            p = self.doc.new_tag('p')
            p.string = repl
            a.replace_with(p)

    def transform_sources(self):
        source = self.site.find('div', class_=re.compile('article-module--sources--'))
        source.unwrap()

    def transform(self):
        self.transform_strong()
        self.transform_italic()
        self.transform_img()
        self.transform_a()
        # self.transform_h2()
        # self.transform_h3()
        self.transform_sources()


class Untools(Extractor):
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
