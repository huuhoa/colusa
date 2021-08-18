from colusa.etr import Extractor, register_extractor


@register_extractor('//agilethought.com')
class AgileThoughtExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('div', attrs={'data-elementor-type': 'single'})

    def cleanup(self):
        first_div = self.site.find('div', class_="elementor-section-wrap")
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
