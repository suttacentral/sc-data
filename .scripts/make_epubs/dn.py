import regex
import lxml.html
from epub import Book
from common import make_clean_html, epubcheck

title = 'Long Discourses'
author = 'Bhante Sujato'
cover = 'cover.png'

cover_page = '''
<div>
<img src="../images/cover.png" alt="Dhamma Wheel"/>
</div>
'''

introduction_page = '''
<h1>Long Discourses</h1>

<p>This is a draft eBook based on the translations by Bhante Sujato from suttacentral.net, it is not for distribution</p>
'''

stylesheet = '''
'''

outfile = 'dn-predraft.epub'

book = Book(title=title, author=author)
book.add_stylesheet('\n')
book.add_image(name='cover.png', data=open(cover, 'rb').read())
book.add_page(title=title, content=cover_page, uid='cover')
title_page = book.add_page(title='Introduction', content=introduction_page, uid='intro')

for uid in [f'dn{i}' for i in range(1, 35)]:
    chapter_content = make_clean_html(uid)
    chapter_title = regex.search('<h1>(.*)</h1>', chapter_content)[1].strip()
    chapter = book.add_page(title=chapter_title, content=chapter_content, uid='uid)

book.save(outfile)
epubcheck(outfile)
