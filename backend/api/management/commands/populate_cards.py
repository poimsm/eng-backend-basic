from django.core.management.base import BaseCommand
from api.models import InfoCard, ResourceSentence, SourceTypes, Collocation

from django.conf import settings
import traceback
from api.helpers import console, read_JSON_file


class Command(BaseCommand):
    help = 'Create info cards'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    POPULATE CARDS              ')
        console.info('--------------------------------')

        try:
            console.info('Reading cards JSON file...')
            cards = read_JSON_file('data/cards/cards.json')

            AUDIO_URL = settings.SITE_DOMAIN + '/media/card_audios/'
            IMAGE_URL = settings.SITE_DOMAIN + '/media/card_images/'

            console.info('Audio base URL: ' + AUDIO_URL)

            counter = 0
            for ex in cards:
                if ex['is_new']:
                    counter += 1

            console.info('Creating ' + str(counter) + ' cards...')

            for card in cards:
                if not ex['is_new']:
                    continue

                card_obj = InfoCard(
                    id=card['id'],
                    group=card['group'],
                    image_url=IMAGE_URL + card['image_file'],
                    voice_url=AUDIO_URL + card['audio_file']
                )

                card_obj.save()

                for sen in card['sentences']:
                    ResourceSentence(
                        sentence=sen['sentence'],
                        meaning=sen['meaning'],
                        extras=sen['extras'],
                        type=sen['type'],
                        source_type=SourceTypes.INFO_CARD,
                        info_card=card_obj
                    ).save()

                for coll in card['collocations']:
                    Collocation(
                        text=coll,
                        source_type=SourceTypes.INFO_CARD,
                        info_card=card_obj
                    ).save()

            console.info('Successfully completed!')

        except:
            traceback.print_exc()
            console.error('Process Failed!')
