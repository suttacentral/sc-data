import regex

def prune_html(html_string):
    html_string = regex.sub(r'(?s)^.*<body.*?>\s*', r'', html_string)
    html_string = regex.sub(r'(?s)</body>.*', r'', html_string)
    return html_string

def rewrite_html(html_string):
    if "'" in html_string:
        html_string = regex.sub(r"'(s|t|ve|eva)", r"’\1", html_string)
        
    if "'" in html_string:
        raise ValueError
        for m in regex.finditer(r'=".*?"', html_string):
            if "'" in m[0]:
                print('Problematic HTML attribute: {m[0]}')
    return html_string.replace('"', "'")

def monolithic_markup_to_segment_markup(markup_string):
    markup_string = markup_string.replace('\n', '')
    
    result = {}
    for m in regex.finditer(r'(?sm)(.*?{)(.*?)(}\s*(?:<br>|(?:</\w+>\s*)*)\n*)', markup_string):
        segment_id = m[2]
        segment_markup = m[1] + m[3]
        result[segment_id] = segment_markup
        

    tail = markup_string[m.end(0):]
    result[segment_id] += tail

    return result

def segmented_markup_to_monolithic(segment_data):
    result = []
    for segment_id, markup in segment_data.items():
        if regex.search(r'</(?:p|h1|h2|h3|h4|h5|h6|blockquote|div|article|section|header)>', markup) or '<br>' in markup:
            markup += '\n'
        result.append(markup.replace('{}', '{' + segment_id + '}'))
    
    string = ''.join(result)
    return string