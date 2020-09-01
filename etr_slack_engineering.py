from etr import Extractor


class SlackEngineeringExtractor(Extractor):
    def get_title(self):
        title = self.bs.find('h1')
        return title.text

    def internal_init(self):
        self.site = self.bs.find(id='primary', class_='main-content')
