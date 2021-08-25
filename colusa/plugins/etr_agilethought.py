from bs4 import Tag

from colusa.etr import Extractor, register_extractor


@register_extractor('//agilethought.com')
class AgileThoughtExtractor(Extractor):
    def _find_main_content(self) -> Tag:
        return self.bs.find('div', attrs={'data-elementor-type': 'single'})

    def cleanup(self):
        first_div = self.main_content.find('div', class_="elementor-section-wrap")
        if first_div is None:
            super(Extractor, self).cleanup()
            return

        section_counter = 0
        to_removed = []
        for section in first_div.contents:
            if section.name != 'section':
                continue
            if section_counter != 2:
                to_removed.append(section)

            section_counter += 1
        for section in to_removed:
            section.extract()

    def _parse_author(self):
        yoast_data = self.bs.find('script', attrs={
            'type': "application/ld+json",
            'class': "yoast-schema-graph",
        })
        if yoast_data is None:
            return super(AgileThoughtExtractor, self)._parse_author()
        import json
        data = json.loads(yoast_data.string)
        graph = data.get('@graph', [])
        persons = {}
        author = None
        for g in graph:
            g_type = g.get('@type', '')
            if g_type == 'Article':
                author = g.get('author', {}).get('@id')
            if g_type == 'Person':
                person_id = g.get('@id', '')
                person_name = g.get('name', '')
                persons[person_id] = person_name
        if author in persons:
            return persons[author]
        return None
