# -*- coding: utf-8 -*-
"""API for traversing the document nodes. Implemented by the compiler and
meta introspection.
"""

from bs4 import PageElement, NavigableString, Tag

from colusa import logs


class NodeVisitor(object):
    """Walks the abstract syntax tree and call visitor functions for every
    node found.  The visitor functions may return values which will be
    forwarded by the `visit` method.

    Per default the visitor functions for the nodes are ``'visit_'`` +
    class name of the node.  So a `TryFinally` node visit function would
    be `visit_TryFinally`.  This behavior can be changed by overriding
    the `get_visitor` function.  If no visitor function exists for a node
    (return value `None`) the `generic_visit` visitor is used instead.
    """

    def get_visitor(self, node: PageElement):
        """Return the visitor function for this node or `None` if no visitor
        exists for this node.  In that case the generic visit function is
        used instead.
        """
        if type(node) is NavigableString:
            method = "visit_text"
        elif type(node) is Tag:
            method = f"visit_tag_{node.name}"
        else:
            method = "visit_unknown"
        value = getattr(self, method, None)
        if value is None:
            logs.warn('Cannot get visit method:', method)
        return value

    def visit(self, node, *args, **kwargs):
        """Visit a node."""
        f = self.get_visitor(node)
        if f is not None:
            return f(node, *args, **kwargs)
        return self.generic_visit(node, *args, **kwargs)

    def visit_text(self, node, *args, **kwargs):
        return node.string

    def visit_unknown(self, node, *args, **kwargs):
        logs.warn('UNKNOWN Node Type:', node.__class__.__name__)
        return ''

    def generic_visit(self, node, *args, **kwargs):
        """Called if no explicit visitor function exists for a node."""
        if node is None:
            return ''

        content = []
        try:
            for child in node.contents:
                value = self.visit(child, *args, **kwargs)
                content.append(value)
        except TypeError as e:
            logs.error(e)
        return ''.join(content)
