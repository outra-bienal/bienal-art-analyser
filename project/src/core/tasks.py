import subprocess
from unipath import Path
from urllib.parse import urlparse
import shlex

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


def yolo_detect_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    filename = db_image.image.name.split('/')[-1]
    clean_filename = filename.split('.')[0]
    temp_file = Path('/', 'tmp', filename)

    with open(temp_file, 'bw') as fd:
        fd.write(db_image.image.read())

    pred_file = Path(settings.DARKNET_DIR, 'pred-{}.png'.format(clean_filename))
    command = ' '.join([
        settings.DARKNET_BIN,
        'detect',
        settings.YOLO_CONF,
        settings.YOLO_WEIGHTS,
        temp_file,
        '-out',
        pred_file.name.split('.')[0],
    ])
    print('Exec --> {}'.format(command))

    detect = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=settings.DARKNET_DIR,
    )
    detect.wait()

    db_image.write_yolo_file(pred_file)
    db_image.save()

    temp_file.remove()
    pred_file.remove()
    print('Success!')
