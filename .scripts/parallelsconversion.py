import json
import re
from typing import Tuple

INPUT_FILE = 'parallels.json'
OUTPUT_FILE = 'new_parallels.json'

EMPTY_ENTRY = lambda: {"full": [], "resembling": [], "retells": [], "mentions": [], "sections": {}}
EMPTY_SECTION = lambda: {"full": [], "resembling": [], "retells": [], "mentions": []}


def natural_sort_key(s):
    if not isinstance(s, str):
        print(f"Not a string: {type(s)} = {s}")
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def add_unique(existing: list, new_items: list) -> list:
    return list(set(existing + new_items))


def split_full_resembling(parlist: list) -> Tuple[list, list]:
    """Split a list into full parallels and resembling parallels."""
    full, resembling = [], []
    for item in parlist:
        if item.startswith("~"):
            resembling.append(item.lstrip("~"))
        else:
            full.append(item)
    return full, resembling


def update_entry(entry: dict, partype: str, new_parlist: list) -> None:
    """Update a parallel entry (top-level or section) in-place."""
    if partype == "retell":
        entry["retells"] = add_unique(entry["retells"], new_parlist)
    elif partype == "mention":
        entry["mentions"] = add_unique(entry["mentions"], new_parlist)
    else:
        full_list, resembling_list = split_full_resembling(new_parlist)
        entry["full"] = add_unique(entry["full"], full_list)
        entry["resembling"] = add_unique(entry["resembling"], resembling_list)


def parseitem(newpardict: dict, parlist: list, partype: str) -> None:
    if partype == "mention":
        parlist = [i.lstrip("~") for i in parlist]

    for paritem in parlist:
        if paritem.startswith("~"):
            continue

        suttauid = paritem.split("#", 1)[0]
        newpardict.setdefault(suttauid, EMPTY_ENTRY())

        new_parlist = [i for i in parlist if i != paritem]

        if "#" not in paritem:
            update_entry(newpardict[suttauid], partype, new_parlist)
        else:
            sections = newpardict[suttauid]["sections"]
            sections.setdefault(paritem, EMPTY_SECTION())
            update_entry(sections[paritem], partype, new_parlist)


def main():
    with open(INPUT_FILE, 'r', encoding='utf8') as f:
        parallelsobject = json.load(f)

    newpardict = {}

    for item in parallelsobject:
        if "parallels" in item:
            parseitem(newpardict, item["parallels"], "parallel")
        elif "mentions" in item:
            parseitem(newpardict, item["mentions"], "mention")
        elif "retells" in item:
            parseitem(newpardict, item["retells"], "retell")
        else:
            print(f"Warning: unrecognised item structure: {item}")

    for entry in newpardict.values():
        entry["sections"] = dict(sorted(entry["sections"].items(), key=lambda x: natural_sort_key(x[0])))

    with open(OUTPUT_FILE, 'w', encoding='utf8') as f:
        json.dump(dict(sorted(newpardict.items(), key=lambda x: natural_sort_key(x[0]))), f, ensure_ascii=False, indent=8)

if __name__ == "__main__":
    main()