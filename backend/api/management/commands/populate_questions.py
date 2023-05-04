# Framework
from django.core.management.base import BaseCommand
from django.conf import settings
import traceback

# Custom
from api.models import Question, Style, Category, Supercategory
from api.helpers import console, read_JSON_file


class Command(BaseCommand):
    help = 'Create questions'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    POPULATE QUESTIONS          ')
        console.info('--------------------------------')

        try:
            console.info('Reading questions JSON file...')
            questions = read_JSON_file('data/questions/questions.json')

            AUDIO_URL = settings.SITE_DOMAIN + '/media/question_audios/'
            IMAGE_URL = settings.SITE_DOMAIN + '/media/question_images/'

            console.info('Audio base URL: ' + AUDIO_URL)

            counter = 0
            for q in questions:
                if q['for_prod'] and q['ready']:
                    counter += 1

            console.info('Creating ' + str(counter) + ' questions...')

            for q in questions:
                if q['for_prod'] and not q['ready']:
                    continue

                difficultyDic = {
                    'easy': 0,
                    'moderate': 1,
                    'complex': 2,
                }

                Question(
                    id=q['id'],
                    question=q['question'],
                    voice_url=AUDIO_URL + q['voice_file'],
                    has_image=q['has_image'],
                    image_url= IMAGE_URL + q['image_file'],
                    difficulty=difficultyDic[q['difficulty']],
                    type=q['type']
                ).save()

                question = Question.objects.get(id=q['id'])

                for cat in q['categories']:
                    cat_obj = Category.objects.get(name=cat)
                    question.categories.add(cat_obj)

                for cat in q['super_categories']:
                    supcat_obj = Supercategory.objects.get(name=cat)
                    question.supercategories.add(supcat_obj)

                Style(
                    background_screen=q['style']['background_screen'],
                    background_challenge=q['style']['background_challenge'],
                    use_gradient=q['style']['use_gradient'],
                    bottom_gradient_color=q['style']['bottom_gradient_color'],
                    top_gradient_color=q['style']['top_gradient_color'],
                    question_position=q['style']['question_position'],
                    image_position=q['style']['image_position'],
                    question_font_size=q['style']['question_font_size'],
                    question_opacity=q['style']['question_opacity'],
                    question=question
                ).save()
                

            console.info('Successfully completed!')

        except:
            traceback.print_exc()
            console.error('Process Failed!')
