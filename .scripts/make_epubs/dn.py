import regex
import lxml.html
from epub import Book
from po_to_html import make_clean_html

title = 'Long Discourses'
author = 'Bhante Sujato'
cover = 'cover.png'

introduction_page = '''
<h1>Long Discourses</h1>

<p>This is a draft eBook based on the translations by Bhante Sujato from suttacentral.net, it is not for distribution</p>
'''

stylesheet = '''
'''


book = Book(title=title, author=author)
with open(cover, 'br') as f:
    book.add_cover(f.read())
book.add_stylesheet('\n')
title_page = book.add_page(title='Introduction', content=introduction_page)

for uid in [f'dn{i}' for i in range(1, 35)]:
    chapter_content = make_clean_html(uid)
    chapter_title = regex.search('<h1>(.*)</h1>', chapter_content)[1].strip()
    chapter = book.add_page(title=chapter_title, content=chapter_content)

book.save('dn-predraft.epub')