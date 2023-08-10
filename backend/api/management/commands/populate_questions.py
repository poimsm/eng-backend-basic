# Framework
from django.core.management.base import BaseCommand
from django.conf import settings
import traceback

# Custom
from api.models import Question, Style, Word
from api.helpers import console, read_JSON_file, make_prefix


class Command(BaseCommand):
    help = 'Create questions'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    POPULATE QUESTIONS          ')
        console.info('--------------------------------')

        try:
            console.info('Reading questions JSON file...')
            questions = read_JSON_file('data/questions.json')

            console.info('Creating ' + str(len(questions)) + ' questions...')

            for q in questions:
                print('Populatin question ID: ' + str(q['id']))

                difficulty_level = {
                    'easy': 0,
                    'moderate': 1,
                    'complex': 2,
                }

                media = settings.SITE_DOMAIN + '/media'
                folder = 'questions/' + make_prefix(q['id'])

                example = q.get('example', None)

                if q['example']:
                    exam_dir = make_prefix(q['example'])
                    example = read_JSON_file(f'data/examples/' + exam_dir + '/index.json')
                    example['voice_url'] = f'{media}/{folder}/example.mp3'

                
                # scenario = {} if q['type'] == 3 else None
                scenario = q.get('scenario', None)

                if scenario:
                    for i, part in enumerate(scenario['parts']):
                        part_options = part.get('options', None)
                        part_voice = part.get('voice_url', None)
                        part_image = part.get('image_url', None)

                        if part_image:
                            scenario['parts'][i]['image_url'] =  f'{media}/{folder}/{part_image}'

                        if part_voice:
                            scenario['parts'][i]['voice_url'] =  f'{media}/{folder}/{part_voice}'

                        if part_options:
                            for j, opt in enumerate(part_options):
                                opt_img = opt['image_url']
                                if opt_img:
                                    scenario['parts'][i]['options'][j]['image_url'] =  f'{media}/{folder}/{opt_img}'                

                Question(
                    id=q['id'],
                    question=q['question'],
                    voice_url=f'{media}/{folder}/voice.mp3',
                    image_url=f'{media}/{folder}/image.webp',
                    difficulty=difficulty_level[q['difficulty']],
                    notes=q['help'],
                    type=q['type'],
                    example=example,
                    scenario=scenario,
                    status= 1 if q['ready'] else 0
                ).save()

                question = Question.objects.get(id=q['id'])

                for word_id in q['words']:
                    word = Word.objects.get(id=word_id)
                    question.words.add(word)

                Style(
                    background_screen=q['style']['background_screen'],
                    background_challenge=q['style']['background_challenge'],
                    question=question
                ).save()

            console.info('Successfully completed!')

        except:
            traceback.print_exc()
            console.error('Process Failed!')
