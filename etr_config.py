"""
etr_config: load configuration for doing ETR
"""

from etr import Extractor
import re


class JsonConfigExtractor(Extractor):
    def __init__(self, config, bs):
        self.config = config.get('extractor', {})
        super(JsonConfigExtractor, self).__init__(bs)

    def get_title(self):
        if 'title' not in self.config:
            return super(JsonConfigExtractor, self).get_title()

        tag = self.bs.find(self.config['title']['tag'], attrs=self.config['title']['attrs'])
        rex = re.compile(r'\n\s*')
        text = re.sub(rex, ' ', tag.text)
        return text

    def internal_init(self):
        self.site = self.bs.find(self.config.get('content', {}).get('tag', ''), attrs=self.config.get('content', {}).get('attrs', {}))
