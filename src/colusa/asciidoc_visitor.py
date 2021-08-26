import re

import requests
from bs4 import Tag

from .utils import download_image
from .visitor import NodeVisitor


class AsciidocVisitor(NodeVisitor):
    def text_cleanup(self, text: str) -> str:
        text = text.strip()
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', text)
        return text

    def visit_TagHeading(self, node, level, text, *args, **kwargs):
        text = self.text_cleanup(text)
        if not text:
            # empty heading
            return '\n\n'

        return f'{"="*(level+1)} {text}\n\n'

    def visit_tag_fall_through(self, node, *args, **kwargs):
        return self.generic_visit(node, *args, **kwargs)

    def visit_tag_ignore_content(self, node, *args, **kwargs):
        return ''

    visit_tag_span = visit_tag_fall_through
    visit_tag_section = visit_tag_fall_through
    visit_tag_input = visit_tag_fall_through

    visit_tag_iframe = visit_tag_ignore_content
    visit_tag_style = visit_tag_ignore_content
    visit_tag_svg = visit_tag_ignore_content
    visit_Stylesheet = visit_tag_ignore_content
    visit_Comment = visit_tag_ignore_content
    visit_tag_button = visit_tag_ignore_content
    visit_tag_form = visit_tag_ignore_content
    visit_tag_script = visit_tag_ignore_content

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
        if len(node.contents) == 1:
            child = node.contents[0]
            if type(child) is Tag and child.name == 'img':
                # anchor around image, should ignore the anchor
                return text

        return f'link:{href}[{text}]'

    def visit_tag_p(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        return f'{text}\n\n'

    visit_tag_article = visit_tag_p
    visit_tag_div = visit_tag_p

    def visit_heading_node(level):
        def visitor(self, node, *args, **kwargs):
            text = self.generic_visit(node, *args, **kwargs)
            text = self.text_cleanup(text)
            if not text:
                # empty heading
                return '\n\n'

            return f'\n{"=" * (level + 1)} {text}\n\n'

        return visitor

    visit_tag_h1 = visit_heading_node(2)
    visit_tag_h2 = visit_heading_node(2)
    visit_tag_h3 = visit_heading_node(3)
    visit_tag_h4 = visit_heading_node(4)

    def visit_tag_h5(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        text = self.text_cleanup(text)
        if not text:
            # empty heading
            return '\n\n'

        return f'\n\n**{text}**\n\n'
    visit_tag_h6 = visit_tag_h5

    def visit_tag_strong(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        return self.tag_wrap_around(text, '**')

    visit_tag_b = visit_tag_strong

    def visit_tag_em(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        return self.tag_wrap_around(text, '__')

    visit_tag_i = visit_tag_em

    def tag_wrap_around(self, text, w):
        if not text:
            return ''
        new_text = text.strip()
        if not new_text:
            return ''
        begin, t, end = text.partition(new_text)
        return f'{begin}{w}{t}{w}{end}'

    def visit_tag_blockquote(self, node, *args, **kwargs):
        cite_node = node.find('cite')
        cite = None
        if cite_node is not None:
            cite_node.extract()
            cite = cite_node.text
        text = self.generic_visit(node, *args, **kwargs)
        if cite is None:
            return f'[quote]\n____\n{text}\n____\n\n'
        else:
            return f'[quote, {cite}]\n____\n{text}\n____\n\n'

    def visit_tag_hr(self, node, *args, **kwargs):
        return "\n'''\n\n"

    def visit_tag_br(self, node, *args, **kwargs):
        pre = kwargs.get('pre')
        if len(node.contents) > 0:
            text = self.generic_visit(node, *args, **kwargs)
        else:
            text = ''

        if not pre:
            return f"\n\n{text}"
        else:
            return f"\n{text}"

    def visit_tag_ol(self, node, *args, **kwargs):
        return self.wrapper_list(node, 'ol', *args, **kwargs)

    def visit_tag_ul(self, node, *args, **kwargs):
        return self.wrapper_list(node, 'ul', *args, **kwargs)

    def wrapper_list(self, node, list_type, *args, **kwargs):
        indent = kwargs.get('indent', 0)
        indent = indent + 1
        indent_stack = kwargs.get('indent_stack', [])
        indent_stack.append(list_type)
        kwargs['indent'] = indent
        kwargs['indent_stack'] = indent_stack
        text = self.generic_visit(node, *args, **kwargs)
        indent = indent - 1
        indent_stack.pop()
        kwargs['indent'] = indent
        kwargs['indent_stack'] = indent_stack
        return f'{text}\n\n'

    def visit_tag_li(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        if not text:
            return ''

        indent = kwargs.get('indent', 1)
        indent_stack = kwargs.get('indent_stack', [])
        if len(indent_stack) == 0:
            # something wrong, ignore data
            return ''
        last = indent_stack[-1]
        if last == 'ul':
            sep = '*'
        else:
            sep = '.'
        return f'{sep*indent} {text}\n'

    def visit_tag_figure(self, node, *args, **kwargs):
        caption_node = node.find('figcaption')
        if caption_node is not None:
            kwargs['caption'] = caption_node.text
            caption_node.extract()
        # specialized for medium
        node_to_visit = node
        if 'paragraph-image' in node.get('class', []):
            noscript = node.find('noscript')
            if noscript is not None:
                node_to_visit = noscript
        text = self.generic_visit(node_to_visit, *args, **kwargs)
        if caption_node is not None:
            del kwargs['caption']
        return f'{text}\n\n'

    def visit_tag_img(self, node, *args, **kwargs):
        alt = node.get('alt', '')
        height = node.get('height', '')
        width = node.get('width', '')
        src = node.get('src')
        if src is None:
            return ''
        srcset = node.get('srcset')
        dim = f'{width}, {height}'
        dim, src = self.get_image_from_srcset(srcset, src, dim)
        url_path = requests.compat.urljoin(kwargs['src_url'], src)
        if not (url_path.startswith('http://') or url_path.startswith('https://')):
            return ''
        image_name = download_image(url_path, kwargs['output_dir'])

        caption = kwargs.get('caption')
        href = kwargs.get('href')
        if not href:
            href_str = ''
        else:
            href_str = f'[link={href}]\n'
        if not caption:
            return f'{href_str}image:{image_name}[{alt},{dim}]'
        else:
            return f'.{caption}\n{href_str}image:{image_name}[{alt},{dim}]\n'

    def get_image_from_srcset(self, srcset, default_src, default_dim):
        import re

        if srcset is None:
            return default_dim, default_src

        srcs = srcset.split(',')
        imgs = {}
        for s in srcs:
            s = s.strip()
            ss = s.split(' ')
            if len(ss) > 1:
                imgs[ss[1]] = ss[0]
        if len(imgs) == 0:
            return default_dim, default_src

        dim_list = sorted(imgs.keys(), key=lambda x: float(re.sub('w|h|x', '', x)))
        largest = dim_list[-1]
        src = imgs[largest]
        dim = default_dim
        if 'w' in largest:
            dim = f"{largest.replace('w', '')},"
        if 'h' in largest:
            dim = f",{largest.replace('w', '')}"

        return dim, src

    def visit_tag_pre(self, node, *args, **kwargs):
        kwargs['pre'] = True
        text = self.generic_visit(node, *args, **kwargs)
        del kwargs['pre']
        return f'''[listing]
....
{text}
....

'''

    def visit_tag_code(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        if '\n' in text:
            # multiline code
            lang = node.get('class', ['text'])
            lang = lang[0]
            lang = lang.replace('language-', '')
            ascii_content = f'''[source, {lang}]
----
{text}
----
'''
            return ascii_content
        else:
            # inline
            return f'`{text}`'

    def visit_tag_table(self, node, *args, **kwargs):
        all_tr = node.find_all('tr')
        table = []
        headers = []
        num_cols = 0
        for tr in all_tr:
            all_td = []
            for td in tr.contents:
                if td.name == 'td':
                    text = self.generic_visit(td, *args, **kwargs)
                    all_td.append(text)
                if td.name == 'th':
                    text = self.generic_visit(td, *args, **kwargs)
                    headers.append(text)
            if num_cols == 0:
                num_cols = len(all_td)
            table.append(all_td)
        if len(headers) == 0:
            option_header = '%noheader'
        else:
            option_header = '%header'
        option_cols = ','.join(['1' for _ in range(num_cols)])

        table_preamble = '|==='
        table_close = '|==='
        r_table = [f'[{option_header},cols="{option_cols}"]', table_preamble]
        if len(headers) > 0:
            r_header = '\n'.join([f'| {h}' for h in headers]) + '\n'
            r_table.append(r_header)
        for row in table:
            r_row = '\n'.join([f'a| {c}' if len(c) > 0 else '|' for c in row]) + '\n'
            r_table.append(r_row)
        r_table.append(table_close)
        r_table.append('\n')
        render_text = '\n'.join(r_table)
        return render_text
