
def translate_to_hugging_face_format(data, file_name, classes_to_ids):
    translated_data = {
        "file_name": file_name,
        "objects": {
            "bbox": [],
            "category": []
        }
    }

    for item in data:
        bounding_box = item["boundingBox"]
        category_type = item["type"]
        category = classes_to_ids.get(category_type, 2)

        x_min, y_min, x_max, y_max = bounding_box
        width = x_max - x_min
        height = y_max - y_min
        translated_data["objects"]["bbox"].append([x_min, y_min, width, height])
        translated_data["objects"]["category"].append(category)

    return translated_data
