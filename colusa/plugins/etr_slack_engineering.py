from colusa.etr import Extractor, register_extractor


@register_extractor('//slack.engineering')
class SlackEngineeringExtractor(Extractor):
    def _parse_title(self):
        title = self.bs.find('h1')
        return title.text

    def _find_main_content(self):
        return self.bs.find(id='primary', class_='main-content')
