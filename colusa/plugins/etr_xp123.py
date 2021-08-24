from colusa.etr import Extractor, register_extractor


@register_extractor('//xp123.com')
class XP123Extractor(Extractor):
    def __init__(self, bs):
        self.author = None
        self.published = None
        super(XP123Extractor, self).__init__(bs)

        self._parse_yoast()

    def internal_init(self):
        self.site = self.bs.find('article', attrs={'class': 'post'})

    def cleanup(self):
        self.remove_tag(self.site, 'header', attrs={'class': 'entry-header'})
        self.remove_tag(self.site, 'section', attrs={'class': 'yikes-mailchimp-container'})
        self.remove_tag(self.site, 'footer', attrs={'class': 'entry-meta'})

    def get_author(self):
        return self.author if self.author else super(XP123Extractor, self).get_author()

    def get_published(self):
        return self.published if self.published else super(XP123Extractor, self).get_published()

    def _parse_yoast(self):
        yoast_data = self.bs.find('script', attrs={
            'type': "application/ld+json",
            'class': "yoast-schema-graph",
        })
        if yoast_data is None:
            return

        import json
        from dateutil import parser
        data = json.loads(yoast_data.string)
        graph = data.get('@graph', [])
        persons = {}
        author = None
        for g in graph:
            g_type = g.get('@type', '')
            if g_type == 'Article':
                author = g.get('author', {}).get('@id')
                published_value = g.get('datePublished')
                if published_value:
                    published = parser.parse(published_value)
                    self.published = str(published.date())

            if (type(g_type) is list and 'Person' in g_type) or (type(g_type) is str and g_type == 'Person'):
                person_id = g.get('@id', '')
                person_name = g.get('name', '')
                persons[person_id] = person_name
        if author in persons:
            self.author = persons[author]

