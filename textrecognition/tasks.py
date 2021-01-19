from Model.pre_post_process_image import process_photo
from textrecognition.celery import app
import random
import logging
from PIL import Image
from numpy import asarray
from django.core.files import File
import base64
from io import BytesIO
import sys
from base64 import b64encode
from celery.signals import setup_logging
import cv2


@setup_logging.connect
def config_loggers(*args, **kwargs):
	from logging.config import dictConfig
	from django.conf import settings
	dictConfig(settings.LOGGING)


@app.task
def recognize(b64_image):
	logger = logging.getLogger('celery')
	logger.debug("recognition started")

	img_encoded = b64_image.encode('utf-8')
	img = base64.b64decode(img_encoded)

	image = Image.open(BytesIO(img))
	data = asarray(image)
	logger.debug(data.shape)

	if len(data.shape) > 2 and data.shape[2] == 4:
		data = cv2.cvtColor(data, cv2.COLOR_BGRA2BGR)
	
	sys.argv = [sys.argv[0]]
	
	output_image, colored_sentences = process_photo(data)
	logger.debug(output_image)
		
	logger.debug(colored_sentences)


	img_uri = numpyimg_to_uri(output_image)
	return img_uri, colored_sentences



@app.task
def hi():
	a = 5
	b = 6
	c = a+b

def numpyimg_to_uri(numpy_img):
    img = Image.fromarray(numpy_img, 'RGB')
    databytes = BytesIO()
    img.save(databytes, "JPEG")
    data64 = b64encode(databytes.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')