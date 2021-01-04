from re import Match
from typing import Type
from xml.etree.ElementTree import Element

import markdown
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import AtomicString


class UnderscoreToItalicLangPattern(Pattern):

    def __init__(self, pattern: str, md: Markdown):
        super(UnderscoreToItalicLangPattern, self).__init__(pattern, md)

    def handleMatch(self, match: Match) -> Element:
        groups = match.groupdict()
        element: Element = markdown.util.etree.Element('i')
        element.set('lang', 'pi')
        element.set('translate', 'no')
        element.text = AtomicString(groups.get('text'))
        return element


class UnderscoreToItalicLangExtension(Extension):
    PATTERN = r'\_(?P<text>.*?)\_'

    def add_inline(self, md: Markdown, name: str, pattern_class: Type[UnderscoreToItalicLangPattern]) -> None:
        pattern = pattern_class(self.PATTERN, md)
        md.inlinePatterns.register(pattern, name, 175)

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        self.add_inline(md, 'UnderscoreToItalicLangExtension', UnderscoreToItalicLangPattern)
