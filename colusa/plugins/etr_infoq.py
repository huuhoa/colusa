from colusa.etr import Extractor, register_extractor


@register_extractor('//www.infoq.com')
class InfoQExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('div', class_='article__content')

    def cleanup(self):
        self.remove_tag(self.site, 'div', attrs={'class': 'contentRatingWidget'})
        self.remove_tag(self.site, 'div', attrs={'class': 'widget article__fromTopic topics'})
        self.remove_tag(self.site, 'div', attrs={'class': 'nocontent'})
        super(InfoQExtractor, self).cleanup()
