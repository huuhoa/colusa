# -*- coding: utf-8 -*-
"""API for traversing the document nodes. Implemented by the compiler and
meta introspection.
"""

from typing import Any, Callable, Optional

from bs4 import PageElement, NavigableString, Tag, BeautifulSoup

from colusa import logs


class NodeVisitor:
    """Walks the abstract syntax tree and call visitor functions for every
    node found.  The visitor functions may return values which will be
    forwarded by the `visit` method.

    Per default the visitor functions for the nodes are ``'visit_'`` +
    class name of the node.  So a `TryFinally` node visit function would
    be `visit_TryFinally`.  This behavior can be changed by overriding
    the `get_visitor` function.  If no visitor function exists for a node
    (return value `None`) the `generic_visit` visitor is used instead.
    """

    def get_visitor(self, node: PageElement) -> Optional[Callable[..., str]]:
        """Return the visitor function for this node or `None` if no visitor
        exists for this node.  In that case the generic visit function is
        used instead.
        
        Args:
            node: The BeautifulSoup page element to get visitor for
            
        Returns:
            The visitor method or None if not found
        """
        if type(node) is NavigableString:
            method = "visit_text"
        elif type(node) is Tag:
            method = f"visit_tag_{node.name}"
        elif type(node) is BeautifulSoup:
            method = 'visit_BeautifulSoup'
        else:
            method = "visit_unknown"
        value = getattr(self, method, None)
        if value is None:
            logs.warn('Cannot get visit method:', method)
        return value

    def visit(self, node: PageElement, *args: Any, **kwargs: Any) -> str:
        """Visit a node.
        
        Args:
            node: The node to visit
            *args: Additional positional arguments passed to visitor
            **kwargs: Additional keyword arguments passed to visitor
            
        Returns:
            String result from visiting the node
        """
        f = self.get_visitor(node)
        if f is not None:
            return f(node, *args, **kwargs)
        return self.generic_visit(node, *args, **kwargs)

    def visit_text(self, node: NavigableString, *args: Any, **kwargs: Any) -> str:
        """Visit a text node.
        
        Args:
            node: The NavigableString text node
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            The text content of the node
        """
        return node.string or ''

    def visit_unknown(self, node: PageElement, *args: Any, **kwargs: Any) -> str:
        """Visit an unknown node type.
        
        Args:
            node: The unknown node
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Empty string
        """
        logs.warn('UNKNOWN Node Type:', node.__class__.__name__)
        return ''

    def visit_BeautifulSoup(self, node: BeautifulSoup, *args: Any, **kwargs: Any) -> str:
        """Visit a BeautifulSoup root node.
        
        Args:
            node: The BeautifulSoup root node
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Result of generic_visit on the node
        """
        return self.generic_visit(node, *args, **kwargs)

    def generic_visit(self, node: Optional[PageElement], *args: Any, **kwargs: Any) -> str:
        """Called if no explicit visitor function exists for a node.
        
        Args:
            node: The node to visit generically
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Concatenated results from visiting all child nodes
        """
        if node is None:
            return ''

        content: list[str] = []
        try:
            for child in node.contents:
                value = self.visit(child, *args, **kwargs)
                content.append(value)
        except TypeError as e:
            logs.error(e)
        return ''.join(content)
