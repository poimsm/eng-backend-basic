from django.core.management.base import BaseCommand
from api.models import Question, Word

from django.conf import settings
import traceback
from api.helpers import console


class Command(BaseCommand):
    help = 'Delete all questions, words, (and examples/styles by cascade)'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    DELETE QUESTIONS            ')
        console.info('--------------------------------')

        try:

            console.info('Deleting quesitons...')
            questions = Question.objects.all()
            for q in questions:
                q.words.clear()

            Question.objects.all().delete()
            Word.objects.all().delete()

            console.info('Successfully completed!')

        except:
            traceback.print_exc()
            console.error('Process Failed!')
