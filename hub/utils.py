
hub_regexp = r"(%([a-zA-z_-]*)(?:\?=)?([a-z]*)%)"

def safe_extract(key_name, obj, ret):
    if key_name not in obj.keys():
        return ret

    return obj[key_name]
