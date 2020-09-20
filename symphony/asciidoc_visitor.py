import re

import requests

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

    visit_tag_span = visit_tag_fall_through
    visit_tag_iframe = visit_tag_fall_through

    def visit_tag_a(self, node, *args, **kwargs):
        href = node.get('href', '')
        text = self.generic_visit(node, *args, **kwargs)
        m = re.match(r'https?://', href)
        if m is None:
            return text
        else:
            return f'link:{href}[{text}]'

    def visit_tag_p(self, node, *args, **kwargs):
        text = self.generic_visit(node, *args, **kwargs)
        return f'{text}\n\n'

    visit_tag_div = visit_tag_p
    visit_tag_figure = visit_tag_p

    def visit_heading_node(level):
        def visitor(self, node, *args, **kwargs):
            text = self.generic_visit(node, *args, **kwargs)
            text = self.text_cleanup(text)
            if not text:
                # empty heading
                return '\n\n'

            return f'{"=" * (level + 1)} {text}\n\n'

        return visitor

    visit_tag_h1 = visit_heading_node(1)
    visit_tag_h2 = visit_heading_node(2)
    visit_tag_h3 = visit_heading_node(3)
    visit_tag_h4 = visit_heading_node(4)
    visit_tag_h5 = visit_heading_node(5)
    visit_tag_h6 = visit_heading_node(6)

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

    def visit_tag_img(self, node, *args, **kwargs):
        alt = node.get('alt', '')
        height = node.get('height', '')
        width = node.get('width', '')
        src = node.get('src', None)
        if src is None:
            return ''
        srcset = node.get('srcset', None)
        dim = f'{width}, {height}'
        dim, src = self.get_image_from_srcset(srcset, src, dim)
        url_path = requests.compat.urljoin(kwargs['src_url'], src)
        image_name = download_image(url_path, kwargs['output_dir'])
        return f'image:{image_name}[{alt},{dim}]'

    def get_image_from_srcset(self, srcset, default_src, default_dim):
        if srcset is None:
            return default_dim, default_src

        srcs = srcset.split(', ')
        imgs = {}
        for s in srcs:
            s = s.strip()
            ss = s.split(' ')
            if len(ss) > 1:
                imgs[ss[1]] = ss[0]
        if len(imgs) == 0:
            return default_dim, default_src

        dim_list = sorted(imgs.keys(), key=lambda x: int(x.replace('w', '').replace('h', '')))
        largest = dim_list[-1]
        src = imgs[largest]
        dim = default_dim
        if 'w' in largest:
            dim = f"{largest.replace('w', '')},"
        if 'h' in largest:
            dim = f",{largest.replace('w', '')}"

        return dim, src
