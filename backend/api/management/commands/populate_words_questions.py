from django.core.management.base import BaseCommand
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join

from api.models import (
    Word, Question
)

class Command(BaseCommand):
    help = 'Migrate words'

    def handle(self, *args, **kwargs):

        print('---------------------------------')
        print(' POPULATE WORDS FROM QUESTIONS   ')
        print('---------------------------------')
        
        try:
            path = 'data/categories/mixed'
            mixed = [f for f in listdir(path) if isfile(join(path, f))]
            
            for mx in mixed:
                
                file = open(os.path.join(settings.BASE_DIR, path + mx))
                words = []
                for line in file.readlines():
                    word = line.strip()
                    if word != '':
                        words.append(word.lower())
                file.close()


                quesiton_id = mx.replace('.txt', '').split('_')[1]
                question_obj = Question.objects.first(id=quesiton_id)

                for word in set(words):
                    word_obj, _ = Word.objects.get_or_create(
                        word=word,
                        in_use=True,
                    )

                    question_obj.words.add(word_obj)

            print('Successfully completed!')

        except Exception as err:
            raise SystemExit(err)
