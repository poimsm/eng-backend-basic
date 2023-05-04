from django.core.management.base import BaseCommand
from django.conf import settings

import os
from os import listdir
from os.path import isfile, join
import json


from api.models import (
    Category, Supercategory
)


class Command(BaseCommand):
    help = 'Migrate categories'

    def handle(self, *args, **kwargs):

        print('--------------------------------')
        print('      POPULATE CATEGORIES       ')
        print('--------------------------------')

        try:
            print('Creating in-use categories...')
            in_use_path = 'data/categories/in_use'
            in_use_cats = [f for f in listdir(
                in_use_path) if isfile(join(in_use_path, f))]

            for cat in in_use_cats:
                Category(
                    name=cat.replace('.txt', ''),
                    in_use=True,
                ).save()

            print('Creating bait categories...')
            bait_path = 'data/categories/bait'
            bait_cats = [f for f in listdir(
                bait_path) if isfile(join(bait_path, f))]

            for cat in bait_cats:
                Category(
                    name=cat.replace('.txt', ''),
                    in_use=False,
                ).save()

            print('Creating supercategories...')
            f = open('data/categories/super_cats.json')
            supercategories = json.load(f)
            f.close()

            for supercat in supercategories:

                if not supercat['ready']:
                    continue

                Supercategory(
                    name=supercat['name'],
                ).save()

                supercat_obj = Supercategory.objects.get(name=supercat['name'])

                print('Bait categories...')
                for cat in supercat['bait']:
                    Category.objects.get(
                        name=cat).supercategories.add(supercat_obj)

                print('Hidden categories...')
                for cat in supercat['hidden']:
                    Category.objects.get(
                        name=cat).supercategories.add(supercat_obj)

                print('Exposed categories...')
                for cat in supercat['exposed']:
                    Category.objects.get(
                        name=cat).supercategories.add(supercat_obj)

            print('Successfully completed!')

        except Exception as err:
            raise SystemExit(err)
