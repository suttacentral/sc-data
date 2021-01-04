from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


class StarToEmphasizeExtension(Extension):
    PATTERN = r'(\*{1})(.*?)\1'

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.inlinePatterns.register(SimpleTagInlineProcessor(self.PATTERN, 'em'), 'em', 175)
