import markdown

from .extensions import (
    DeregisterStandardFunctionsExtension,
    DoubleStarsToBoldExtension,
    StarToEmphasizeExtension,
    UnderscoreToItalicLangExtension,
    ReplaceDefaultParagraphExtension,
)

EXTENSIONS = [
    DeregisterStandardFunctionsExtension(),
    ReplaceDefaultParagraphExtension(),
    DoubleStarsToBoldExtension(),
    StarToEmphasizeExtension(),
    UnderscoreToItalicLangExtension(),
]

MD = markdown.Markdown(
    extensions=EXTENSIONS,
    output_format='html',
)


def parse(text: str) -> str:
    transformed_text = MD.convert(text)
    transformed_text = transformed_text\
        .replace('<REPLACE_TAG>', '')\
        .replace('</REPLACE_TAG>', '')\
        .replace('&lt;', '<')\
        .replace('&gt;', '>')
    return transformed_text
