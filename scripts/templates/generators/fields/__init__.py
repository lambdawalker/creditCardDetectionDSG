from scripts.templates.generators.fields.field_generators import (
    generate_credit_card, generate_payment_network,
    get_random_bank, get_random_card_name,
    get_random_card_phrase,
    get_random_flavor,
    generate_random_valid_thru
)

from scripts.templates.generators.fields.generate_logo import get_random_payment_network_logo
from scripts.templates.generators.fields.get_random_person_name import get_random_person_name

field_generators = {
    # Text
    "creditCardNumber": generate_credit_card,
    "paymentNetworkName": generate_payment_network,
    "bankName": get_random_bank,
    "card_name": get_random_card_name,
    "benefit": get_random_card_phrase,
    "cardFlavor": get_random_flavor,
    "userName": get_random_person_name,
    "expirationDate": generate_random_valid_thru,

    # Images
    "paymentNetworkLogo": get_random_payment_network_logo,
}


