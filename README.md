# vector-ocr
This simple project uses Vector’s camera to capture an image containing a printed sentence, Tesseract OCR for image-to-text and Vector’s say_text() to speak the result.

Note that the image is heavily pre-processed before OCR and that accuracy of the result depends a lot on the distance the page is placed in front of Vector (should be about 20 cm away), lighting conditions, font size/type etc. The code contains several filters that you can experiment with that may work better under different conditions.

