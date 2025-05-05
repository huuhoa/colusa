from colusa.etr import Extractor, register_extractor


@register_extractor('//archive.md')
class ArchiveExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', attrs={'js-target':'article-content'})

    def cleanup(self):
        # self.remove_tag(self.main_content, 'div', attrs={'class': 'contentRatingWidget'})
        # self.remove_tag(self.main_content, 'div', attrs={'class': 'widget article__fromTopic topics'})
        # self.remove_tag(self.main_content, 'div', attrs={'class': 'nocontent'})
        super(ArchiveExtractor, self).cleanup()
