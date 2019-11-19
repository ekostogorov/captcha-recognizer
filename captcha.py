import os
import cv2
import uuid
import time
import requests
import pytesseract

from bs4 import BeautifulSoup as bso
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops

class CaptchaRecognizer:
  pass_factor: int = 55
  folder: str = './tmp'

  def __init__(self, pass_factor: int = None, folder: str = None):
    if pass_factor:
      self.pass_factor = pass_factor
    if folder:
      self.folder = folder

    self._check_or_create_dir()

  def _check_or_create_dir(self):
    if not os.path.isdir(self.folder):
      os.mkdir(self.folder)

  def recognize(self, filename: str) -> str:
    cleaned = self._remove_noise(filename)

    img = cv2.imread(cleaned, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_LINEAR)
    img = cv2.medianBlur(img, 9)
    th, img = cv2.threshold(img, 185, 255, cv2.THRESH_BINARY)
    cv2.imwrite("image.png", img)

    text = pytesseract.image_to_string(
      image=img,
      lang='eng',
      config='--psm 8 --dpi 70 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    
    self._clean_folder()

    text = "".join(i for i in text if i.isalnum())
    return text.strip()
    
  def _remove_noise(self, filename: str) -> str:
    img = Image.open(filename)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    if 'L' != img.mode:
      img = img.convert('L')

    for column in range(img.size[0]):
      for line in range(img.size[1]):
          value = self._remove_noise_by_pixel(img, column, line)
          img.putpixel((column, line), value)

    output = self.folder + '/' + self._create_filename() + '.png'
    img.save(output)
    
    return output

  def _remove_noise_by_pixel(self, img, column, line):
    if img.getpixel((column, line)) < self.pass_factor:
        return (0)
    return (255)

  def _clean_folder(self):
    for filename in os.listdir(self.folder):
      filepath = os.path.join(self.folder, filename)

      print(filepath)
      os.remove(filepath)

  def _create_filename(self) -> str:
    uid = uuid.uuid4()
    return str(uid)