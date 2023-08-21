def find_non_ASCII(s):
    for idx, i in enumerate(s):
        if 0 <= ord(i) <= 127:
            continue
        else:
            return idx
    return -1


def get_first_children(o):
    try:
        c = next(o.children)
        return c
    except:
        return None
