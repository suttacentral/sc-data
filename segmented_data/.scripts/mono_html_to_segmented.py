import json
import pathlib

from html_lib import prune_html, rewrite_html, monolithic_markup_to_segment_markup


files = list(pathlib.Path("../markup/").glob("**/*.html"))

for file in files:
    html_string = file.open().read()

    html_string = rewrite_html(html_string)
    html_string = prune_html(html_string)
    result = monolithic_markup_to_segment_markup(html_string)

    new_file = file.with_suffix('.json')
    with new_file.open('w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    file.unlink()