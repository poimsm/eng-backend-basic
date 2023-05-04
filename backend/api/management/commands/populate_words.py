from django.core.management.base import BaseCommand
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join

from api.models import (
    Word, Category
)

class Command(BaseCommand):
    help = 'Migrate words'

    def handle(self, *args, **kwargs):

        print('--------------------------------')
        print('      POPULATE WORDS            ')
        print('--------------------------------')
        
        try:
            path = 'data/categories/in_use'        
            categories = [f for f in listdir(path) if isfile(join(path, f))]           

            print('Reading all words per category...')
            
            for cat in categories:
                
                file = open(os.path.join(settings.BASE_DIR,
                            'data/categories/in_use/' + cat))
                words = []
                for line in file.readlines():
                    word = line.strip()
                    if word != '':
                        words.append(word.lower())
                file.close()

                category_obj = Category.objects.first(name=cat.replace('.txt', ''))

                for word in set(words):
                    word_obj, _ = Word.objects.get_or_create(
                        word=word,
                        in_use=False,
                    )
                    # word_obj = Word.objects.create(word=word, in_use=False)
                    # word_obj.save()
                    # saved_id = word_obj.id

                    word_obj.categories.add(category_obj)

                    # if user.partner_set.filter(slug=requested_slug).exists():
                    #     # do some private stuff

                    # if user in partner.user.all():
                    #     #do something

                    # Word(
                    #     word=word,
                    #     category=category_obj
                    # ).save()

            print('Successfully completed!')

        except Exception as err:
            raise SystemExit(err)
