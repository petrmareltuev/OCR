from django.http import HttpResponse
from django.shortcuts import render
import logging
from PIL import Image
from numpy import asarray
from base64 import b64encode
from io import BytesIO
import sys
from textrecognition.tasks import recognize,hi
from textrecognition.settings import CELERY_BROKER_URL, CELERY_BROKER_TRANSPORT_OPTIONS
from kombu import Connection, Producer, Consumer
import base64
# Create your views here.

def fuf():
	logger = logging.getLogger(__name__)
	logger.debug(hello)
	return "tutut"

def home_view(request, *args, **kwargs):

	
	logger = logging.getLogger(__name__)
	

	if request.method == 'POST':

		logger.debug('recognition request ')
		uploaded_image = request.FILES['image_to_process']
		logger.debug(type(uploaded_image))
		data64 = base64.b64encode(uploaded_image.file.read())
		recognize.delay(data64.decode('utf-8'), __name__)

		return render(request, 'image.html', {"image": 'sdf', "sentences": {}})
	
	return render(request, "home.html", {})

def numpyimg_to_uri(numpy_img):
    img = Image.fromarray(numpy_img, 'RGB')
    databytes = BytesIO()
    img.save(databytes, "JPEG")
    data64 = b64encode(databytes.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')

