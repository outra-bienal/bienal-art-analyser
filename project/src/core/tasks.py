from src.core import analysers


def analyse_image_task(analysed_image_id):
    from src.core.models import AnalysedImage
    try:
        db_image = AnalysedImage.objects.get(id=analysed_image_id)
    except AnalysedImage.DoesNotExist:
        return None

    if not db_image.recokgnition_result:
        result = analysers.aws_analyser(db_image.image.url)
        if result:
            db_image.recokgnition_result = result
            db_image.save(update_fields=['recokgnition_result'])
