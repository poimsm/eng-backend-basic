from django.core.management.base import BaseCommand
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
from api.helpers import console, read_JSON_file, make_prefix
import traceback

from api.models import (
    Word
)

def list_subdirectories(directory):
    subdirectories = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    return subdirectories

class Command(BaseCommand):
    help = 'Migrate words'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('      POPULATE WORDS            ')
        console.info('--------------------------------')
        
        try:
            # word_dir = 'data/words'
            word_paths  = list_subdirectories('data/words')
            # print(word_paths)
            # return
            # word_file_names = [f for f in listdir(word_dir) if isfile(join(word_dir, f))]

            console.info(f'Reading {len(word_paths)} words...')
            
            for path in word_paths:
                id = int(path.split('/')[2])
                print('Populatin word ID: ' + str(id))

                folder = 'words/' + path.split('/')[2]
                media = f'{settings.SITE_DOMAIN}/media'

                wordJSON = read_JSON_file(f'{path}/index.json')               
                translations = read_JSON_file(f'{path}/word_translation.json')

                miniature = wordJSON['miniature']
                miniature['image_url'] = f"{media}/{folder}/mini.jpg"
                
                examples = []
                for i, ex in enumerate(wordJSON['examples']):
                    examples.append({
                        'value': ex['value'],
                        'voice_url': f'{media}/{folder}/ex_0{i + 1}.mp3',
                        'translations': read_JSON_file(f'{path}/ex_translation_0{i+1}.json')
                    })

                explanations = [{
                    'image': None,
                    'value': wordJSON['explanations'][0]['value'],
                    'translations': read_JSON_file(f'{path}/explanation_translation.json')
                }]              

                # explanations = []
                # for i, expl in enumerate(wordJSON['explanations']):
                #     explan = expl
                #     if 'image' in expl:
                #         explan['image'] = f"{media}/{folder}/ex_{expl['image']}"
                #     explanations.append(explan)

                # story = None
                # if wordJSON['story']:
                #     story = wordJSON['story']
                #     story['voice_url']  = f'{media}/{folder}/story.mp3'
                #     story['image']      = f'{media}/{folder}/story.jpg'
                #     story['cover']      = f'{media}/{folder}/story_cover.jpg'

                Word(
                    # id=wordJSON['id'],
                    id=id,
                    word=wordJSON['word'],
                    definition=wordJSON['definition'],
                    translations=translations,
                    miniature=miniature,
                    examples=examples,
                    explanations=explanations,
                    story=None,
                    status= 1 if wordJSON['ready'] else 0
                ).save()

            console.info('Successfully completed!')

        except Exception as err:
            traceback.print_exc()
            console.error('Process Failed!')
            # raise SystemExit(err)
