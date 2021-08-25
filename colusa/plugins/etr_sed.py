from colusa.etr import Extractor, register_extractor


@register_extractor('https://softwareengineeringdaily.com/')
class SoftwareEngineeringDailyExtractor(Extractor):
    def _find_main_content(self):
        self.site = self.bs.find('main')
