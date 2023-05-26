from django.core.management.base import BaseCommand
from django.conf import settings
from os import listdir
from os.path import isfile, join
from api.helpers import console, read_JSON_file, make_prefix
import traceback

from api.models import (
    Word
)

class Command(BaseCommand):
    help = 'Migrate words'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('      POPULATE WORDS            ')
        console.info('--------------------------------')
        
        try:
            word_dir = 'data/words'
            word_file_names = [f for f in listdir(word_dir) if isfile(join(word_dir, f))]

            console.info(f'Reading {len(word_file_names)} words...')
            
            for file_name in word_file_names:
                wordJSON = read_JSON_file(f'{word_dir}/{file_name}')               

                folder = 'words/' + make_prefix(wordJSON['id'])
                media = f'{settings.SITE_DOMAIN}/media'

                miniature = wordJSON['miniature']
                miniature['image_url'] = f"{media}/{folder}/mini.png"
                
                examples = []
                for i, ex in enumerate(wordJSON['examples']):
                    exam = ex
                    exam['voice_url'] = f'{media}/{folder}/ex_0{i + 1}.mp3'
                    examples.append(exam)

                explanations = []
                for i, expl in enumerate(wordJSON['explanations']):
                    explan = expl
                    if 'image' in expl:
                        explan['image'] = f"{media}/{folder}/ex_{expl['image']}"
                    explanations.append(explan)

                story = None
                if wordJSON['story']:
                    story = wordJSON['story']
                    story['voice_url']  = f'{media}/{folder}/story.mp3'
                    story['image']      = f'{media}/{folder}/story.png'
                    story['cover']      = f'{media}/{folder}/story_cover.png'

                Word(
                    id=wordJSON['id'],
                    word=wordJSON['word'],
                    definition=wordJSON['definition'],
                    translations=wordJSON['translations'],
                    has_info=wordJSON['has_info'],
                    miniature=miniature,
                    examples=examples,
                    explanations=explanations,
                    story=story
                ).save()

            console.info('Successfully completed!')

        except Exception as err:
            traceback.print_exc()
            console.error('Process Failed!')
            # raise SystemExit(err)
