# https://stackoverflow.com/questions/66463612/how-to-find-table-grid-lines-in-pdf-files
import pdfplumber
import cv2 as cv
import numpy as np
import random


import torch
import torchvision
from torchvision.io import read_image
from torchvision.utils import draw_bounding_boxes

# Application
# from PyQt6.QtWidgets import QApplication, QWidget
# "vertical_strategy": "text"
pdf = pdfplumber.open('Statement_12_2025_box.pdf')
p0 = pdf.pages[0] # go to the required page

tables = p0.debug_tablefinder() # list of tables which pdfplumber identifies
req_table = tables.tables[0] # Suppose you want to use ith table

cells = req_table.cells # gives list of all cells in that table

box = []
for i in cells:
    box.append(list(i))
print(box)


# drawing 
import fitz
doc = fitz.open('Statement_12_2025.pdf')
for page in doc:
    for i in box:
        rect = fitz.Rect(i) 
        page.draw_rect(i,  color = (0, 1, 0), width = 2)
doc.save('Statement_12_2025_box.pdf')