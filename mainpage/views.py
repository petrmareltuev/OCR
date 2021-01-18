from django.http import HttpResponse
from django.shortcuts import render, redirect
import logging
from PIL import Image
from PIL import UnidentifiedImageError
from numpy import asarray
from base64 import b64encode
from io import BytesIO
import sys
from textrecognition.tasks import recognize
import base64
from celery import group
from django.utils.datastructures import MultiValueDictKeyError
from celery.result import AsyncResult

def home_view(request, *args, **kwargs):

	logger = logging.getLogger(__name__)
	logger.debug( request.method)

	if request.method == 'POST':

		logger.debug('recognition request ')
		
		try:
			uploaded_image = request.FILES['image_to_process']
			logger.debug(uploaded_image.size)
			if (uploaded_image.size > 10000000):
				return render(request, "home.html", {'message':'Слишком большой размер файла!'})
		except MultiValueDictKeyError:
			return render(request, "home.html", {'message':'Изображение не загружено'})
		data64 = base64.b64encode(uploaded_image.file.read())
		result = recognize.delay(data64.decode('utf-8'))
		res = recognize.AsyncResult(result.task_id)
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
		try:
			img, c_sent = res.get()
		except UnidentifiedImageError:
			logger.debug('UnidentifiedImageError')
			return render(request, 'home.html', {})

		#sentences = [["Hello from dajngo", "(240,240,100)"],["Group sentences", "(123,123,123)"]]
		sents = [["hi", "rgb(234,234,100)"], ["hello", "rgb(123,123,123)"]]
		data = {"image": img, "sents": c_sent}
		logger.debug(data)
		return render(request, 'image.html', context = data)

	return render(request, "processing.html", {"taskId" : uuid})

def handler404(request, template_name="404.html"):
    response = render(request, template_name, {})
    response.status_code = 404
    return response

def handler500(request, template_name="500.html"):
    response = render(request, template_name, {})
    response.status_code = 500
    return response
