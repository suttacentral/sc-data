from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


class DoubleStarsToBoldExtension(Extension):
    PATTERN = r'(\*{2})(.*?)\1'

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.inlinePatterns.register(SimpleTagInlineProcessor(self.PATTERN, 'b'), 'b', 175)
