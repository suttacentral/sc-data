from markdown import Markdown
from markdown.extensions import Extension


class DeregisterStandardFunctionsExtension(Extension):

    PREPROCESSORS = [
        # 'normalize_whitespace',
        # 'html_block',
    ]

    BLOCK_PROCESSORS = [
        'empty',
        'indent',
        'code',
        'hashheader',
        'setextheader',
        'hr',
        'olist',
        'ulist',
        'quote',
        'reference',
        'paragraph',
    ]

    INLINE_PATTERNS = [
        'backtick',
        'escape',
        'reference',
        'link',
        'image_link',
        'image_reference',
        'short_reference',
        'short_image_ref',
        'autolink',
        'automail',
        'linebreak',
        'html',
        'entity',
        'not_strong',
        'em_strong',
        'em_strong2',
    ]

    TREE_PROCESSORS = [
        # 'inline',
        # 'prettify',
    ]

    POSTPROCESSORS = [
        # 'raw_html',
        # 'amp_substitute',
        # 'unescape',
    ]

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)

        for preprocessor in self.PREPROCESSORS:
            md.preprocessors.deregister(preprocessor)

        for block_processor in self.BLOCK_PROCESSORS:
            md.parser.blockprocessors.deregister(block_processor)

        for inline_pattern in self.INLINE_PATTERNS:
            md.inlinePatterns.deregister(inline_pattern)

        for tree_processor in self.TREE_PROCESSORS:
            md.treeprocessors.deregister(tree_processor)

        for postprocessor in self.POSTPROCESSORS:
            md.postprocessors.deregister(postprocessor)
