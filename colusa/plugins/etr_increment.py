from colusa.etr import Extractor, register_extractor


@register_extractor('//increment.com')
class IncrementDotComExtractor(Extractor):
    def _parse_title(self):
        title = self.bs.find('h1', class_='t-TitleSerif large title')
        return title.text

    def _find_main_content(self):
        return self.bs.find('article', attrs={'itemprop': 'articleBody'})

    def _parse_extra_metadata(self):
        author_tag = self.bs.find('a', attrs={'itemprop': 'author'})
        if author_tag is None:
            author = ''
        else:
            author = author_tag.text

        description = self.bs.find('div', attrs={'itemprop': 'description'})
        if description is None:
            return ''

        return f'author: **{author}**\n\n{description.text}\n'
