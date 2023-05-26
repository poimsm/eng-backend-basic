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
                difficultyDic = {
                    'easy': 0,
                    'moderate': 1,
                    'complex': 2,
                }

                media = settings.SITE_DOMAIN + '/media'
                folder = 'questions/' + make_prefix(q['id'])

                exam_file = make_prefix(q['example']) + '.json'
                example = read_JSON_file(f'data/examples/' + exam_file)
                example['voice_url'] = f'{media}/{folder}/example.mp3'

                Question(
                    id=q['id'],
                    question=q['question'],
                    voice_url=f'{media}/{folder}/voice.mp3',
                    image_url=f'{media}/{folder}/image.jpg',
                    difficulty=difficultyDic['easy'],
                    example=example,
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
