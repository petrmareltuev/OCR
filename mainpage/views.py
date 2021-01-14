from django.http import HttpResponse
from django.shortcuts import render, redirect
import logging
from PIL import Image
from numpy import asarray
from base64 import b64encode
from io import BytesIO
import sys
from textrecognition.tasks import recognize
import base64
from celery import group
from celery.result import AsyncResult

def home_view(request, *args, **kwargs):

	logger = logging.getLogger(__name__)

	if request.method == 'POST':

		logger.debug('recognition request ')
		uploaded_image = request.FILES['image_to_process']
		data64 = base64.b64encode(uploaded_image.file.read())
		result = recognize.delay(data64.decode('utf-8'))
		res = recognize.AsyncResult(result.task_id)
		logger.debug(res)
		logger.debug(type(res.task_id))

		return redirect(processing, uuid = result.task_id)
		# return render(request, 'processing.html', {"image": 'sdf', "sentences": {}})
	
	return render(request, "home.html", {})


def processing(request, uuid):
	logger = logging.getLogger(__name__)

	logger.debug("processing uuid request")
	logger.debug(uuid)

	res = recognize.AsyncResult(str(uuid))
	logger.debug(res.ready())
	
	if (res.ready()):
		img = res.get()
		return render(request, 'image.html', {"image": img, "sentences": {}})

	return render(request, "processing.html", {"taskId" : uuid})


