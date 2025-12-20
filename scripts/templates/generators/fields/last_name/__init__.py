import os

from scripts.templates.generators.fields.select_word import select_random_word_from_nested_directory


def generate_last_name():
    db_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(db_path, "db") + os.sep

    name, source = select_random_word_from_nested_directory(
        db_path
    )

    return {
        "data": name,
        "source": source
    }
