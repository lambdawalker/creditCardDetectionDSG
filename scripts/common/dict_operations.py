import random


def get_random_member_from_dict(dct: dict, force=None):
    options = tuple(dct.keys())
    choice = random.choice(options) if force is None else force
    return choice, dct[choice]


def find_nested_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            if isinstance(value, dict):
                result = find_nested_key(value, target_key)
                if result is not None:
                    return result
            elif isinstance(value, list):
                for item in value:
                    result = find_nested_key(item, target_key)
                    if result is not None:
                        return result
    elif isinstance(data, list):
        for item in data:
            result = find_nested_key(item, target_key)
            if result is not None:
                return result
    return None
