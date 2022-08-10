import json
import pathlib

from html_lib import segmented_markup_to_monolithic


files = list(pathlib.Path("../markup/").glob("**/*.json"))

for file in files:
    data = json.load(file.open())

    html_string = segmented_markup_to_monolithic(data)
    
    new_file = file.with_suffix('.html')
    with new_file.open('w') as f:
        f.write(html_string)
    file.unlink()