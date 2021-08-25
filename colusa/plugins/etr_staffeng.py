from colusa.etr import Extractor, register_extractor


@register_extractor('//staffeng.com')
class StaffEng(Extractor):
    def _find_main_content(self):
        return self.bs.find(class_='blog-post-content')
