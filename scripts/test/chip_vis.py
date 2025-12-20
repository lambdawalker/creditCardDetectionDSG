import cv2
import random

from scripts.templates.generators.chip_generator import generate_monochromatic_chip

chip_image = generate_monochromatic_chip(n=random.randint(2, 4), image_width=400, padding_percentage=0.05)

cv2.imshow('chip', chip_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
