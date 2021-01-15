import cv2
import numpy as np
import os
from PIL import Image
import paddle
import paddle.distributed as dist

import tools.program as program
from ppocr.data import build_dataloader
from ppocr.modeling.architectures import build_model
from ppocr.postprocess import build_post_process
from ppocr.metrics import build_metric
from ppocr.losses import build_loss
from ppocr.optimizer import build_optimizer
from ppocr.utils.save_load import init_model
from paddleocr import PaddleOCR

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class OCRModel:
    def __init__(self):
        self.ocr_model = PaddleOCR(use_angle_cls=True,
                                   # det='ch_ppocr_server_v1.1_det',
                                   det_model_dir='./pretrained_models/ch_ppocr_server_v2.0_det_infer',
                                   # rec='ch_ppocr_server_v1.1_rec',
                                   rec_model_dir='./pretrained_models/ch_ppocr_server_v2.0_rec_infer',
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

    @staticmethod
    def eval(config_path):
        config = program.load_config(config_path)
        config, device, logger, vdl_writer = program.preprocess(config)
        global_config = config['Global']
        # build dataloader
        valid_dataloader = build_dataloader(config, 'Eval', device, logger)

        # build post process
        post_process_class = build_post_process(config['PostProcess'], global_config)

        # build model for rec algorithm
        if hasattr(post_process_class, 'character'):
            config['Architecture']["Head"]['out_channels'] = len(getattr(post_process_class, 'character'))
        model = build_model(config['Architecture'])

        best_model_dict = init_model(config, model, logger)
        if len(best_model_dict):
            logger.info('metric in ckpt ***************')
            for k, v in best_model_dict.items():
                logger.info('{}:{}'.format(k, v))

        # build metric
        eval_class = build_metric(config['Metric'])

        # start eval
        metirc = program.eval(model, valid_dataloader, post_process_class, eval_class)
        logger.info('metric eval ***************')
        for k, v in metirc.items():
            logger.info('{}:{}'.format(k, v))

    @staticmethod
    def train(config_path):
        config = program.load_config(config_path)
        config, device, logger, vdl_writer = program.preprocess(is_train=True)
        # init dist environment
        if config['Global']['distributed']:
            dist.init_parallel_env()

        global_config = config['Global']

        # build dataloader
        train_dataloader = build_dataloader(config, 'Train', device, logger)
        if config['Eval']:
            valid_dataloader = build_dataloader(config, 'Eval', device, logger)
        else:
            valid_dataloader = None

        # build post process
        post_process_class = build_post_process(config['PostProcess'], global_config)

        # build model for rec algorithm
        if hasattr(post_process_class, 'character'):
            char_num = len(getattr(post_process_class, 'character'))
            config['Architecture']["Head"]['out_channels'] = char_num
        model = build_model(config['Architecture'])
        if config['Global']['distributed']:
            model = paddle.DataParallel(model)

        loss_class = build_loss(config['Loss'])

        optimizer, lr_scheduler = build_optimizer(
            config['Optimizer'],
            epochs=config['Global']['epoch_num'],
            step_each_epoch=len(train_dataloader),
            parameters=model.parameters())

        # build metric
        eval_class = build_metric(config['Metric'])
        # load pretrain model
        pre_best_model_dict = init_model(config, model, logger, optimizer)

        logger.info('train dataloader has {} iters, valid dataloader has {} iters'.
                    format(len(train_dataloader), len(valid_dataloader)))
        # start train
        program.train(config, train_dataloader, valid_dataloader, device, model,
                      loss_class, optimizer, lr_scheduler, post_process_class,
                      eval_class, pre_best_model_dict, logger, vdl_writer)


if __name__ == '__main__':
    img_path = '../Images/img1.png'
    img = np.array(Image.open(img_path), )
    if len(img.shape) > 2 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    ocr = OCRModel()
    print(ocr.recognise_text(img, cls=False))
    # OCRModel.eval("./configs/det/det_mv3_db.yml")
