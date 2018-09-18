from tqdm import tqdm
from datetime import date

from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from src.core.models import Collection, AnalysedImage


class Command(BaseCommand):
    help = _('Cria coleção e faz upload de arquivos no diretório')

    def add_arguments(self, parser):
        parser.add_argument('nome_diretorio_imagens', type=str)

    def handle(self, *args, **kwargs):
        images_dir = settings.LOAD_COLLECTIONS_DIR.child(kwargs['nome_diretorio_imagens'])

        if not images_dir.exists():
            raise CommandError(_('Dir {} não exite.').format(images_dir))
        if not images_dir.isdir():
            raise CommandError(_('{} não é um diretório.').format(images_dir))

        print("Atualizando imagens da análise do Detectron...")
        not_found = []
        for image_file in tqdm(images_dir.listdir()):
            f_name = image_file.name.split('.')[0]
            image_prefix = "{}{}.".format(AnalysedImage.BASE_UPLOAD, f_name)
            try:
                image = AnalysedImage.objects.get(image__startswith=image_prefix)
                image.write_detectron_field(image_file)
                image.save()
            except AnalysedImage.DoesNotExist:
                not_found.append(f_name)

        if not_found:
            names = '\n\t'.join(not_found)
            print('\nNão foi possível encontrar os arquivos: {}'.format(names))
