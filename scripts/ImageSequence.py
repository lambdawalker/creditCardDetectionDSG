import os

from PIL import Image


class ImageSequence:
    def __init__(self, path):
        """
        Initialize with a path to a directory containing images.
        """
        if not os.path.isdir(path):
            raise ValueError(f"The path '{path}' is not a valid directory.")

        self.path = path

        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}

        self.image_files = sorted([
            f for f in os.listdir(path)
            if os.path.splitext(f)[1].lower() in valid_extensions
        ])

    def __len__(self):
        """
        Returns the total number of valid images in the folder.
        """
        return len(self.image_files)

    def __getitem__(self, index):
        """
        Returns the image at the specified index as a PIL Image object.
        """
        if index > len(self) - 1:
            raise IndexError(f"Index {index} is out of range for sequence of length {len(self)}.")

        file_name = self.image_files[index]
        full_path = os.path.join(self.path, file_name)
        return Image.open(full_path)
