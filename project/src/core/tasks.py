import cv2
import shlex
import subprocess
from unipath import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage

from src.core import analysers
from src.core import tag_image


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


def deep_ai_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.deep_ai_analyser(db_image.image.url)
    if result:
        db_image.deep_ai_result = result
        db_image.save(update_fields=['deep_ai_result'])


def clarifai_analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    result = analysers.clarifai_analyser(db_image.image.url)
    if result:
        db_image.clarifai_result = result
        db_image.save(update_fields=['clarifai_result'])


def yolo_detect_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    filename = db_image.image.name.split('/')[-1]
    clean_filename = filename.split('.')[0]
    temp_file = settings.TEMP_DIR.child(filename)

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
        #stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL,
        cwd=settings.DARKNET_DIR,
    )
    detect.wait()

    db_image.write_yolo_file(pred_file)
    db_image.save()

    temp_file.remove()
    pred_file.remove()
    print('Success!')


def generate_dense_cap_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    filename = db_image.image.name.split('/')[-1]
    temp_file = settings.TEMP_DIR.child(filename)

    with open(temp_file, 'bw') as fd:
        fd.write(db_image.image.read())

    captions = db_image.deep_ai_result['DenseCap']['output']['captions']
    all_img = cv2.imread(temp_file))
    limited_img = cv2.imread(temp_file))
    for i, caption in enumerate(captions):
        label = caption['caption']
        p1, p2 = tag_image.get_caption_positions(all_img, caption)
        all_img = tag_image.tag_element(all_img, p1, p2, label)
        if i < 10:
            limited_img = tag_image.tag_element(limited_img, p1, p2, label)

    # image with all captions
    cv2.imwrite(temp_file, all_img)
    db_image.write_dense_cap_full_image(temp_file)

    # image with 10 captions
    cv2.imwrite(temp_file, limited_img)
    db_image.write_dense_cap_image(temp_file)

    db_image.save()
    temp_file.remove()
