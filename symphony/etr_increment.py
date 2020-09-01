from symphony.etr import Extractor


class IncrementDotComExtractor(Extractor):
    def get_title(self):
        title = self.bs.find('h1', class_='t-TitleSerif large title')
        return title.text

    def internal_init(self):
        self.site = self.bs.find('article', attrs={'itemprop': 'articleBody'})

    def get_metadata(self):
        author_tag = self.bs.find('a', attrs={'itemprop': 'author'})
        if author_tag is None:
            author = ''
        else:
            author = author_tag.text

        description = self.bs.find('div', attrs={'itemprop': 'description'})
        if description is None:
            return ''

        return f'author: **{author}**\n\n{description.text}\n'
