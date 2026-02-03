def create_yolo_description(objects, image_width, image_height, classes_to_ids):
    yolo_description = []

    for obj in objects:
        obj_type = obj['class']
        bbox = obj['boundingBox']
        x0, y0, x1, y1 = bbox

        if obj_type not in classes_to_ids:
            raise Exception(f"Object type {obj_type} not recognized")

        class_id = classes_to_ids[obj_type]
        x_center = (x0 + x1) / 2.0 / image_width
        y_center = (y0 + y1) / 2.0 / image_height
        width = (x1 - x0) / image_width
        height = (y1 - y0) / image_height

        yolo_description.append(f"{class_id} {x_center} {y_center} {width} {height}")

    return "\n".join(yolo_description)
