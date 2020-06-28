import regex
from pathlib import Path

from num import DottedNum
from common import print_name_if_needed


def check_ordering(segment_ids, file):
    seen = set()
    for i, line_ids in enumerate(segment_ids):
            for segment_id in line_ids:
                if segment_id in seen:
                    print_name_if_needed(file)
                    prev_id = segment_ids[i-1][0]
                    if i < len(segment_ids) - 1:
                        next_id = segment_ids[i+1][0]
                    else:
                        next_id = None
                    print(f'{segment_id} is duplicate, prev={prev_id}, next={next_id}')
                seen.add(segment_id)

if __name__ == '__main__':
    files = sorted(Path('./html').glob('**/*.html'))

    for file in files:
        with file.open('r') as f:
            lines = f.readlines()


        ssegment_ids = [regex.findall(r'data-uid="[^:]+\:([a-z0-9.^-]+)"', line) for line in lines]
        segment_ids = [s for s in segment_ids if s]

        check_ordering(segment_ids, file)
        
        
