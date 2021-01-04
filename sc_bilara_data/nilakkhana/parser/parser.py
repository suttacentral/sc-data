import markdown

from .extensions import (
    DeregisterStandardFunctionsExtension,
    DoubleStarsToBoldExtension,
    StarToEmphasizeExtension,
    HashToSpanNumExtension,
    UnderscoreToItalicLangExtension,
    HashToSpanCounterExtension,
    ReplaceDefaultParagraphExtension,
)

EXTENSIONS = [
    DeregisterStandardFunctionsExtension(),
    ReplaceDefaultParagraphExtension(),
    DoubleStarsToBoldExtension(),
    StarToEmphasizeExtension(),
    HashToSpanNumExtension(),
    UnderscoreToItalicLangExtension(),
    HashToSpanCounterExtension(),
]

MD = markdown.Markdown(
    extensions=EXTENSIONS,
)


def parse(text: str) -> str:
    transformed_text = MD.convert(text)
    transformed_text = transformed_text.replace('<REPLACE_TAG>', '').replace('</REPLACE_TAG>', '')
    return transformed_text
