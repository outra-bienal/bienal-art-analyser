import subprocess
from unipath import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage

from src.core import analysers


def aws_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.aws_analyser(db_image.image.url)
    if result:
        db_image.recokgnition_result = result
        db_image.save(update_fields=['recokgnition_result'])


def ibm_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.ibm_analyser(db_image.image.url)
    if result:
        db_image.ibm_watson_result = result
        db_image.save(update_fields=['ibm_watson_result'])


def google_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.google_analyser(db_image.image.url)
    if result:
        db_image.google_vision_result = result
        db_image.save(update_fields=['google_vision_result'])


def azure_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.azure_analyser(db_image.image.url)
    if result:
        db_image.azure_vision_result = result
        db_image.save(update_fields=['azure_vision_result'])


def yolo_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    filename = db_image.image.name.split('/')[-1]
    temp_file = Path('/', 'tmp', filename)

    with open(temp_file, 'bw') as fd:
        fd.write(db_image.image.read())

    detect_command = [
        settings.DARKNET_BIN,
        'detect',
        settings.YOLO_CONF,
        settings.YOLO_WEIGHTS,
        temp_file
    ]
    print('Exec --> {}'.format(' '.join(detect_command)))

    detect = subprocess.Popen(
        detect_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=settings.DARKNET_DIR,
    )
    detect.wait()

    pred_file = Path(settings.DARKNET_DIR, 'predictions.png')
    out_filename = '{}.png'.format(filename.split('.')[0])
    with open(pred_file, 'rb') as fd:
        db_image.yolo_image.name = out_filename
        with db_image.yolo_image.open('wb') as out:
            out.write(fd.read())
        db_image.save()

    temp_file.remove()
    pred_file.remove()
    print('Success!')
