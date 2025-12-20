import os
import random

from scripts.templates.generators.fields.select_word import select_random_word_from_nested_directory


def generate_road_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    name_db = os.path.join(db_path, "road/name_db") + os.sep
    type_db = os.path.join(db_path, "road/type_db") + os.sep

    name, name_source = select_random_word_from_nested_directory(name_db)
    road_type, road_type_source = select_random_word_from_nested_directory(type_db)

    return {
        "data": f"{road_type} {name}",
        "source": [road_type_source, name_source]
    }


def generate_block_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    name_db = os.path.join(db_path, "block/name_db") + os.sep
    type_db = os.path.join(db_path, "block/type_db") + os.sep

    name, name_source = select_random_word_from_nested_directory(name_db)
    road_type, road_type_source = select_random_word_from_nested_directory(type_db)

    return {
        "data": f"{road_type} {name}",
        "source": [road_type_source, name_source]
    }


def generate_city_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(db_path, "city") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_state_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(db_path, "state") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_country_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(db_path, "country") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_address_number():
    return {
        "data": str(random.randint(1, 9999)),
        "source": "random/1-9999"
    }
