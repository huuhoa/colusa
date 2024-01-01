from colusa.etr import PostProcessor, register_postprocessor
import re


@register_postprocessor('post-processor.RegexReplace')
class RegexReplaceProcessor(PostProcessor):
    def run(self):
        with open(self.file_path) as fd:
            data = fd.read()

        for kv in self.params:
            print(kv.get('s'))
            data = re.sub(kv.get('s'), kv.get('r'), data, flags=re.MULTILINE)

        with open(self.file_path, 'wt') as fd:
            fd.write(data)

