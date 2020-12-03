from django.http import HttpResponse
from django.shortcuts import render
import logging
from PIL import Image
from numpy import asarray
from base64 import b64encode
from io import BytesIO
from matplotlib import pyplot

# Create your views here.

def home_view(request, *args, **kwargs):

	logger = logging.getLogger(__name__)

	if request.method == 'POST':
		uploaded_image = request.FILES['image_to_process']
		logger.debug("file: {} {}kb".format(uploaded_image.name, uploaded_image.size))

		image = Image.open(uploaded_image)
		logger.debug("image: {} {}".format(image.format, image.size))

		data = asarray(image)
		logger.debug(data.shape)

		data, sentences = data, {(255,0,0): "Hello Petr!",(255,222,0): "How are you?"}

		img_uri = numpyimg_to_uri(data)
		return render(request, 'image.html', {"image": img_uri, "sentences": sentences})
	
	return render(request, "home.html", {})

def numpyimg_to_uri(numpy_img):
    img = Image.fromarray(numpy_img, 'RGB')
    databytes = BytesIO()
    img.save(databytes, "JPEG")
    data64 = b64encode(databytes.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')

