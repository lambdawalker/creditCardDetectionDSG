import random


def rand_int_by_width(image, percentage_lower_limit, percentage_top_limit):
    width = image.size[0]

    return random.randint(
        int(width * percentage_lower_limit / 100),
        int(width * percentage_top_limit / 100)
    )


def get_width_dependent_param(image, percentage_lower_limit, percentage_top_limit, parameter_name, **parameters):
    return parameters.get(
        parameter_name,
        rand_int_by_width(
            image,
            percentage_lower_limit,
            percentage_top_limit
        )
    )


def add_opacity(tuples_list, opacity_value):
    result = []
    for tup in tuples_list:
        result.append((*tup, opacity_value))
    return result
