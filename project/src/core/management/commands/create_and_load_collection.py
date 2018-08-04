from tqdm import tqdm
from datetime import date

from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from src.core.models import Collection, AnalysedImage


class Command(BaseCommand):
    help = _('Cria coleção e faz upload de arquivos no diretório')

    def add_arguments(self, parser):
        parser.add_argument(
            'titulo_colecao',
            type=str,
            help=_('Título da coleção a ser criada.')
        )
        help = _(
            'Nome (relatavio a {}) da coleção a ser criada.'.format(settings.LOAD_COLLECTIONS_DIR)
        )
        parser.add_argument(
            'nome_diretorio_imagens',
            type=str,
            help=help,
        )

    def handle(self, *args, **kwargs):
        collection_title = kwargs['titulo_colecao']
        images_dir = settings.LOAD_COLLECTIONS_DIR.child(kwargs['nome_diretorio_imagens'])

        if not images_dir.exists():
            raise CommandError(_('Dir {} não exite.').format(images_dir))
        if not images_dir.isdir():
            raise CommandError(_('{} não é um diretório.').format(images_dir))
        if Collection.objects.filter(title=collection_title).exists():
            raise CommandError(_('A coleção {} já existe.').format(collection_title))

        print("Creating collection...")
        collection = Collection.objects.create(title=collection_title, date=date.today())
        print("Uploading images...")
        for image_file in tqdm(images_dir.listdir()):
            analysed_image = AnalysedImage(collection=collection)
            analysed_image.write_image_field(image_file)
            analysed_image.save()
