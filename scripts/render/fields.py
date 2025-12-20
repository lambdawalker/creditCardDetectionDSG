from scripts.templates.generators.fields.address import generate_road_name, generate_block_name, generate_address_number, generate_city_name, generate_state_name, generate_country_name
from scripts.templates.generators.fields.first_name import generate_first_name
from scripts.templates.generators.fields.institutions import generate_voting_institution_name
from scripts.templates.generators.fields.last_name import generate_last_name
from scripts.templates.generators.fields.random import choice, generate_hex_string, generate_left_just_number, generate_boolean, generate_int
from scripts.templates.generators.fields.time import generate_date, year_as_number, day_as_number, month_as_number

gen = {
    "name": {
        "first": generate_first_name,
        "last": generate_last_name
    },
    "random": {
        "choice": choice,
        "hex": generate_hex_string,
        "number": generate_int,
        "lf_number": generate_left_just_number,
        "boolean": generate_boolean
    },
    "time": {
        "date": generate_date,
        "year_as_number": year_as_number,
        "day_as_number": day_as_number,
        "month_as_number": month_as_number
    },
    "address": {
        "road": generate_road_name,
        "block": generate_block_name,
        "number": generate_address_number,
        "city": generate_city_name,
        "state": generate_state_name,
        "country": generate_country_name
    },
    "institution": {
        "voting": generate_voting_institution_name
    }
}
