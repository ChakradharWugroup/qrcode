import cv2
from pyzbar.pyzbar import decode
from rapidocr_onnxruntime import RapidOCR
import sys

image_path = sys.argv[1]
print(f"Testing image: {image_path}")

# Read QR
img = cv2.imread(image_path)
decoded_objects = decode(img)
for obj in decoded_objects:
    print("QR Code:", obj.data.decode("utf-8"))

# Read Text
ocr = RapidOCR()
result, elapse = ocr(image_path)
if result:
    for item in result:
        print("Text:", item[1])
