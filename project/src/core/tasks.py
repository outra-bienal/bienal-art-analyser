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
