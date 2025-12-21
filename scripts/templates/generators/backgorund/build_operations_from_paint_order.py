from scripts.common.dict_operations import find_nested_key
from scripts.templates.generators.backgorund import all_operations



def build_operations_from_paint_order(paint_order):
    paint_operations = []

    for operation in paint_order:
        paint_operations.append(
            build_operation_bundle(operation)
        )
    return paint_operations


def build_operation_bundle(operation):
    if operation is None:
        raise Exception("Index out out bounds of Paint orders")

    if isinstance(operation, str):
        operation = {
            "name": operation
        }

    name = operation["name"]
    return name, find_nested_key(all_operations, name), operation


