def flatten(array):
    """
    Flatten a nested list into a single list of elements.

    Parameters:
    array (list): A list which may contain nested lists.

    Returns:
    list: A single flattened list containing all elements.
    """
    flattened_list = []
    for item in array:
        if isinstance(item, list):
            flattened_list.extend(flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list