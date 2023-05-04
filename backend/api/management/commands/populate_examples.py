import traceback
from django.conf import settings
from django.core.management.base import BaseCommand
from api.models import Example, Question
from api.helpers import console, read_JSON_file


class Command(BaseCommand):
    help = 'Create examples'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('     POPULATE EXAMPLES          ')
        console.info('--------------------------------')

        try:
            console.info('Reading index...')
            index = read_JSON_file('data/examples/index.json')

            AUDIO_URL = settings.SITE_DOMAIN + '/media/example_audios/'

            console.info('Audio base URL: ' + AUDIO_URL)

            counter = 0
            for item in index:
                exampleJSON = read_JSON_file(item['example_file_path'])
                for exam in exampleJSON:
                    if exam['is_new']:
                        counter += 1

            console.info('Creating ' + str(counter) + ' examples...')

            for item in index:
                exampleJSON = read_JSON_file(item['example_file_path'])
                for exam in exampleJSON:
                    if not exam['is_new']:
                        continue

                    Example(
                        question=Question.objects.get(id=item['question_id']),
                        voice_url=AUDIO_URL + exam['voice_file'],
                        example=read_JSON_file(exam['subtitles']),
                        sentence_text=exam['word_text']
                    ).save()

            console.info('Successfully completed!')
        except:
            traceback.print_exc()
            console.error('Process Failed!')
