from src.core.models import Collection


def run():
    for collection in Collection.objects.filter(triggered_analysis=True):
        if not collection.processed:
            collection.run_analysis()
