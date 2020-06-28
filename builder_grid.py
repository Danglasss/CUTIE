import numpy as np
import requests
from os import listdir
from matplotlib import image
import json
import sys
import re
from transformers import BertTokenizer

# api key :
# c4e738656f88957
# helloworld

def ocr_space_file(filename, overlay=True, api_key='helloworld', language='eng'):
	payload = {'isOverlayRequired': overlay,
			   'apikey': api_key,
			   'language': language,
			   }
	with open(filename, 'rb') as f:
		r = requests.post('https://api.ocr.space/parse/image',
						  files={filename: f},
						  data=payload,
						  )
	return r.content.decode()

def	get_max_dimension(json_file, line_max):
	count_line = json_file["ParsedResults"][0]["TextOverlay"]["Message"]
	count_line = int(re.findall('\d+', count_line)[0])
	line_max = count_line if count_line > line_max else line_max
	return line_max

def	get_position(invoice_data):
	pos_left  = invoice_data[0]["Words"][0]["Left"] 
	pos_upper = invoice_data[0]["Words"][0]["Top"]
	pos_right = 0
	pos_bot   = 0
	for line in invoice_data:
		for word in line["Words"]:
			left_size  = word["Left"]
			right_size = word["Left"]
			top_size   = word["Top"]
			pos_left  = left_size if left_size < pos_left else pos_left
			pos_right = right_size if right_size > pos_right else pos_right
			pos_upper = top_size if top_size < pos_upper else pos_upper
			pos_bot   = top_size if top_size > pos_bot else pos_bot
	return pos_left, pos_right, pos_upper, pos_bot

def get_file():
	dirFiles = list()
	for filename in listdir('/Users/danglass/Desktop/Image_Dataset'):
		filename = '/Users/danglass/Desktop/Image_Dataset/' + filename
		dirFiles.append(filename)	
	return dirFiles

def	get_data():
	dirFiles = get_file()
	dirFiles.sort(key=lambda f: int(re.sub('\D', '', f)))
	grid_disorder = list()
	invoices_dims = list()
	line_max = 0
	i = 0
	for filename in dirFiles:	
		json_file = json.loads(ocr_space_file(filename))
		invoice_data = json_file["ParsedResults"][0]["TextOverlay"]["Lines"]
		grid_disorder.append(invoice_data)
		line_max = get_max_dimension(json_file, line_max)
		pos_left, pos_right, pos_upper, pos_bot = get_position(invoice_data)
		invoices_dims.append((pos_left, pos_right, pos_upper, pos_bot))		
	return grid_disorder, line_max, invoices_dims

def calcul_x(invoices_dims, pos_left, line_max, width):
	w = invoices_dims[1]
	x_left = pos_left - invoices_dims[0]
	return (10 * (x_left/w))
	
def calcul_y(invoices_dims, top, line_max):
	h = invoices_dims[3] - invoices_dims[2]
	top = top - invoices_dims[2]
	return (18 * (top / h))

def	normalization(wordtext):
	dictionnaire = ["due", "totl", "total", "tota", "payment"]
	wordtext     = wordtext.lower()
	for word in dictionnaire:
		if word == wordtext:
			wordtext = "total"
			break 
	return wordtext

def	build_grid(grid_disorder, line_max, invoices_dims):
	grid_list = np.empty((30, 11),dtype=list)
	for line in grid_disorder:
		for word in line["Words"]:
			wordtext = word["WordText"]
			pos_left = word["Left"]
			width    = word["Width"]
			top      = word["Top"]
			x = calcul_x(invoices_dims, pos_left, line_max, width)
			y = calcul_y(invoices_dims, top, line_max)
			x = round(x)
			y = round(y)
			wordtext = normalization(wordtext)
			grid_list[y][x] = wordtext
	return grid_list

grid_disorder, line_max, invoices_dims = get_data()
i = 0
grid_list = []
for invoice in invoices_dims:
	grid_list.append(build_grid(grid_disorder[i], line_max, invoice))
	print(grid_list[i])
	print("\n\n\n")
	i += 1
