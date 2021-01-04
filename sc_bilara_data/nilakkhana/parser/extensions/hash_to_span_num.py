from re import Match
from typing import Type
from xml.etree.ElementTree import Element

import markdown
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import AtomicString


class HashToSpanNumPattern(Pattern):

    def handleMatch(self, match: Match) -> Element:
        groups = match.groupdict()
        element: Element = markdown.util.etree.Element('span')
        element.set('class', 'num')
        element.text = AtomicString(groups.get('digit'))
        return element


class HashToSpanNumExtension(Extension):
    PATTERN = r'\#(?P<digit>\d+)'

    def add_inline(self, md: Markdown, name: str, pattern_class: Type[HashToSpanNumPattern]) -> None:
        pattern = pattern_class(self.PATTERN, md)
        md.inlinePatterns.register(pattern, name, 175)

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        self.add_inline(md, 'HashToSpanNumExtension', HashToSpanNumPattern)
