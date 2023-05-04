from django.core.management.base import BaseCommand
from api.models import ShortVideo, ResourceSentence, SourceTypes, Collocation

from django.conf import settings
import traceback
from api.helpers import console, read_JSON_file


class Command(BaseCommand):
    help = 'Create short videos'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    POPULATE VIDEOS             ')
        console.info('--------------------------------')

        try:

            console.info('Reading videos JSON file...')

            videos = read_JSON_file('data/videos/videos.json')

            MEDIA_URL = settings.SITE_DOMAIN + '/media/videos/'
            IMAGE_URL = settings.SITE_DOMAIN + '/media/video_images/'

            console.info('Audio base URL: ' + MEDIA_URL)

            counter = 0
            for ex in videos:
                if ex['is_new']:
                    counter += 1

            console.info('Creating ' + str(counter) + ' videos...')

            for video in videos:
                if not ex['is_new']:
                    continue

                video_obj = ShortVideo(
                    id=video['id'],
                    cover=IMAGE_URL + video['cover'],
                    url=MEDIA_URL + video['video_file']
                )

                video_obj.save()

                for sen in video['sentences']:
                    ResourceSentence(
                        sentence=sen['sentence'],
                        meaning=sen['meaning'],
                        extras=sen['extras'],
                        type=sen['type'],
                        source_type=SourceTypes.SHORT_VIDEO,
                        short_video=video_obj
                    ).save()

                for coll in video['collocations']:
                    Collocation(
                        text=coll,
                        source_type=SourceTypes.SHORT_VIDEO,
                        short_video=video_obj
                    ).save()

            console.info('Successfully completed!')

        except:
            traceback.print_exc()
            console.error('Process Failed!')
