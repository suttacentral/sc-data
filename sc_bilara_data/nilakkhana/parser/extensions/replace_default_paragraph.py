from typing import List
from xml.etree.ElementTree import Element, SubElement

from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


class ParagraphProcessor(BlockProcessor):
    """ Process Paragraph blocks. """

    def test(self, parent: Element, block: str):
        return True

    def run(self, parent: Element, blocks: List[str]):
        block = blocks.pop(0)
        if block.strip():
            # Not a blank block. Add to parent, otherwise throw it away.
            if self.parser.state.isstate('list'):
                # The parent is a tight-list.
                #
                # Check for any children. This will likely only happen in a
                # tight-list when a header isn't followed by a blank line.
                # For example:
                #
                #     * # Header
                #     Line 2 of list item - not part of header.
                sibling = self.lastChild(parent)
                if sibling is not None:
                    # Insert after sibling.
                    if sibling.tail:
                        sibling.tail = '{}\n{}'.format(sibling.tail, block)
                    else:
                        sibling.tail = '\n%s' % block
                else:
                    # Append to parent.text
                    if parent.text:
                        parent.text = '{}\n{}'.format(parent.text, block)
                    else:
                        parent.text = block.lstrip()
            else:
                # Create a custom paragraph
                p = SubElement(parent, 'REPLACE_TAG')
                p.text = block.lstrip()


class ReplaceDefaultParagraphExtension(Extension):

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        md.parser.blockprocessors.register(ParagraphProcessor(md.parser), 'paragraph', 10)
