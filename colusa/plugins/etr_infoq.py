from colusa.etr import Extractor, register_extractor


@register_extractor('//www.infoq.com')
class InfoQExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('div', class_='article__content')

    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'contentRatingWidget'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'widget article__fromTopic topics'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'nocontent'})
        super(InfoQExtractor, self).cleanup()
