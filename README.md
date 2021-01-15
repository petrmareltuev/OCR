# OCR

pip install Requirements.txt

# Запуск БД redis
docker run -d -p 6379:6379 redis

# Из папки где лежит manage.py запустить сервер Django:
python manage.py runserver
(может попросить сделать миграции: python manage.py makemigrations)

# Из папки где лежит manage.py запустить сервер celery:
celery -A textrecognition worker -l info

# В браузере на http://127.0.0.1:8000. При первом запросе возможно начнет докачивать зависимости

Положить веса в папку ./pretrained_models/ch_ppocr_server_v2.0_rec_infer/:
https://drive.google.com/file/d/1XPNI5weudFptAHwWdHvsy6Fu-3E_VBch/view?usp=sharing
