from Model.OCRModel import OCRModel
import cv2
import numpy as np
import matplotlib.cm as cm
import itertools
import logging


def process_photo(photo):
    logger = logging.getLogger('celery')
    ocr = OCRModel()
    model_output = ocr.recognise_text(photo, cls=False)
    colors_number = 9 if len(model_output) > 9 else len(model_output)
    colormap = cm.rainbow(np.linspace(0, 1, colors_number))[:, :3] * 255
    color_cycle = itertools.cycle(colormap.astype(int))
    labeled_photo = photo
    colored_sentences = []
    logger.debug(f'sout {model_output}')
    for (single_output, color) in zip(model_output, color_cycle):

        pts = np.array([[int(single_output[0][0][0]),int(single_output[0][0][1])],
            [int(single_output[0][1][0]),int(single_output[0][1][1])],
            [int(single_output[0][2][0]),int(single_output[0][2][1])],
            [int(single_output[0][3][0]),int(single_output[0][3][1])]],
            np.int32)
        pts = pts.reshape((-1, 1, 2))
        labeled_photo = cv2.polylines(labeled_photo,[pts],True,tuple(color.tolist()), thickness =2)

        # labeled_photo = cv2.rectangle(photo,
        #                               (int(single_output[0][0][0]), int(single_output[0][0][1])),
        #                               (int(single_output[0][2][0]), int(single_output[0][2][1])),
        #                               tuple(color.tolist()), 2)
        colored_sentences.append([single_output[1][0], 'rgb' + str(tuple(color))])
    return labeled_photo, colored_sentences
