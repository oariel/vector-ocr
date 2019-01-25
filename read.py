import anki_vector
import time
from PIL import Image
import numpy as np
import cv2
import pytesseract
from anki_vector.util import degrees, distance_mm, speed_mmps
import os

# inspired by this article: https://medium.freecodecamp.org/getting-started-with-tesseract-part-ii-f7f9a0899b3f
def apply_threshold(img, argument):
    switcher = {
        0: cv2.threshold(gray, 48, 255, cv2.THRESH_BINARY)[1],
        1: cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        2: cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        3: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        4: cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        5: cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        6: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        7: cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
    }
    return switcher.get(argument, "Invalid method")


with anki_vector.Robot(enable_camera_feed=True) as robot:

    robot.behavior.set_eye_color(hue=0.83, saturation=0.76)
    robot.behavior.set_head_angle(degrees(20.0))
    robot.behavior.set_lift_height(0.0)

    robot.say_text("Show me the text to read!")

    while not robot.camera.latest_image:
        time.sleep(1.0)

    # Show the image    
    image = robot.camera.latest_image
    image.show()

    robot.say_text("Hold on..")
    image_data = np.asarray(image)

    image_data = cv2.resize(image_data, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # convert to grayscale
    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    gray = cv2.dilate(gray, kernel, iterations=1)
    gray = cv2.erode(gray, kernel, iterations=1)

    # Apply threshold to get image with only black and white
    gray = apply_threshold(gray, 5)
    gray = cv2.medianBlur(gray, 3)

    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    # show the OCR preview
    preview = Image.open(filename)
    preview.show()

    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)
    if not text:
        print('OCR returned no result')
        robot.say_text('Oh no. I can\'t read this text.')
    else:
        print(text)
        robot.say_text('Hey, I can read! ' + text)
