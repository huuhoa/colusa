from colusa.etr import Extractor, register_extractor


@register_extractor('https://softwareengineeringdaily.com/')
class SoftwareEngineeringDailyExtractor(Extractor):
    def _find_main_content(self):
        return self.bs.find('main')
