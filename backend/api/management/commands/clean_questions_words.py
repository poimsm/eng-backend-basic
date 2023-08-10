from django.core.management.base import BaseCommand
from api.helpers import console
import traceback
from django.db import connection


class Command(BaseCommand):
    help = 'Clean all questions and words'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('   CLEANING QUESTIONS & WORDS   ')
        console.info('--------------------------------')
        
        try:
           with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE questions_words, words, styles, questions RESTART IDENTITY CASCADE;')
            console.info('Successfully completed!')

        except Exception as err:
            traceback.print_exc()
            console.error('Process Failed!')
