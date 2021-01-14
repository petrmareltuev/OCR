import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

class OCRModel:
    """
    You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
    to switch the language model.
    """

    def __init__(self):
        self.ocr_model = PaddleOCR(use_angle_cls=True,
                                   det='ch_ppocr_server_v1.1_det',
                                   rec='ch_ppocr_server_v1.1_rec',
                                   cls='ch_ppocr_mobile_v1.1_cls')

    def recognise_text(self, img, det=True, rec=True, cls=True):
        """
        Detects and recognises text on image.
        args：
            img: img for ocr, support ndarray, img_path and list or ndarray
            det: use text detection or not, if false, only rec will be exec. default is True
            rec: use text recognition or not, if false, only det will be exec. default is True
        """
        result = self.ocr_model.ocr(img, det=det, rec=rec, cls=cls)
        return result


if __name__ == '__main__':
    img_path = '../Images/img2.jpg'
    img = np.array(Image.open(img_path))
    ocr = OCRModel()
    print(ocr.recognise_text(img, cls=False))
