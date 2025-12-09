# -*- coding: utf-8 -*-
"""Configuration dataclasses for type-safe configuration handling."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MakeConfig:
    """Configuration for makefile generation (html, epub, pdf targets)."""
    html: str = ''
    epub: str = ''
    pdf: str = ''


@dataclass
class PostProcessingConfig:
    """Configuration for a post-processing step."""
    processor: str
    params: list[Any] = field(default_factory=list)


@dataclass
class PartConfig:
    """Configuration for a book part (used in multi-part books)."""
    title: str
    description: str = ''
    urls: list[str] = field(default_factory=list)


@dataclass
class DownloaderConfig:
    """Configuration for the content downloader."""
    # Extensible for different fetcher configs (e.g., tor, proxy, etc.)
    pass


@dataclass
class BookConfig:
    """Main configuration for generating an ebook.
    
    Attributes:
        title: Book title
        author: Book author
        version: Book version string
        homepage: URL to the book's homepage
        output_dir: Directory for generated output
        book_file_name: Name of the main asciidoc file
        multi_part: Whether the book has multiple parts
        metadata: Whether to include article metadata
        make: Makefile generation settings
        postprocessing: List of post-processing steps
        parts: List of book parts (for multi-part books)
        urls: List of URLs to process (for single-part books)
        book_properties: Additional asciidoc book properties
        title_prefix_trim: Prefix to strip from article titles
        downloader: Downloader configuration
        extractors: Extractor-specific configurations
        transformers: Transformer-specific configurations
    """
    title: str
    author: str
    version: str
    homepage: str
    output_dir: str = '.'
    book_file_name: str = 'index.asciidoc'
    multi_part: bool = False
    metadata: bool = True
    make: MakeConfig = field(default_factory=MakeConfig)
    postprocessing: list[PostProcessingConfig] = field(default_factory=list)
    parts: list[PartConfig] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    book_properties: list[str] = field(default_factory=list)
    title_prefix_trim: str = ''
    downloader: dict[str, Any] = field(default_factory=dict)
    extractors: dict[str, Any] = field(default_factory=dict)
    transformers: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BookConfig':
        """Create a BookConfig from a dictionary (e.g., loaded from JSON/YAML).
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            BookConfig instance with values from the dictionary
        """
        make_data = data.get('make', {})
        make_config = MakeConfig(
            html=make_data.get('html', ''),
            epub=make_data.get('epub', ''),
            pdf=make_data.get('pdf', ''),
        )
        
        postprocessing = [
            PostProcessingConfig(
                processor=pp.get('processor', ''),
                params=pp.get('params', [])
            )
            for pp in data.get('postprocessing', [])
        ]
        
        parts = [
            PartConfig(
                title=part.get('title', ''),
                description=part.get('description', ''),
                urls=part.get('urls', [])
            )
            for part in data.get('parts', [])
        ]
        
        return cls(
            title=data.get('title', ''),
            author=data.get('author', ''),
            version=data.get('version', ''),
            homepage=data.get('homepage', ''),
            output_dir=data.get('output_dir', '.'),
            book_file_name=data.get('book_file_name', 'index.asciidoc'),
            multi_part=data.get('multi_part', False),
            metadata=data.get('metadata', True),
            make=make_config,
            postprocessing=postprocessing,
            parts=parts,
            urls=data.get('urls', []),
            book_properties=data.get('book_properties', []),
            title_prefix_trim=data.get('title_prefix_trim', ''),
            downloader=data.get('downloader', {}),
            extractors=data.get('extractors', {}),
            transformers=data.get('transformers', {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the BookConfig back to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            'title': self.title,
            'author': self.author,
            'version': self.version,
            'homepage': self.homepage,
            'output_dir': self.output_dir,
            'book_file_name': self.book_file_name,
            'multi_part': self.multi_part,
            'metadata': self.metadata,
            'make': {
                'html': self.make.html,
                'epub': self.make.epub,
                'pdf': self.make.pdf,
            },
            'postprocessing': [
                {'processor': pp.processor, 'params': pp.params}
                for pp in self.postprocessing
            ],
            'parts': [
                {'title': p.title, 'description': p.description, 'urls': p.urls}
                for p in self.parts
            ],
            'urls': self.urls,
            'book_properties': self.book_properties,
            'title_prefix_trim': self.title_prefix_trim,
            'downloader': self.downloader,
            'extractors': self.extractors,
            'transformers': self.transformers,
        }
