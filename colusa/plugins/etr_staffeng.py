from colusa.etr import Extractor, register_extractor


@register_extractor('//staffeng.com')
class StaffEng(Extractor):
    def internal_init(self):
        self.site = self.bs.find(class_='blog-post-content')
