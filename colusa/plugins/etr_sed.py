from colusa.etr import Extractor, register_extractor


@register_extractor('https://softwareengineeringdaily.com/')
class SoftwareEngineeringDailyExtractor(Extractor):
    def internal_init(self):
        self.site = self.bs.find('main')
