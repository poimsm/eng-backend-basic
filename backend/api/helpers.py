import json
import os

from django.conf import settings


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class console(object):
    @staticmethod
    def info(msg):
        print(bcolors.BOLD + '[INFO] ' + msg + bcolors.ENDC)

    @staticmethod
    def debug(msg):
        print(bcolors.OKBLUE + '[DEBUG] ' + msg + bcolors.ENDC)

    @staticmethod
    def warning(msg):
        print(bcolors.WARNING + '[WARNING] ' + msg + bcolors.ENDC)

    @staticmethod
    def error(msg):
        print(bcolors.FAIL + '[ERROR] ' + msg + bcolors.ENDC)


def unique(sequence):
    result = []
    for item in sequence:
        if item not in result:
            result.append(item)
    return result


def read_JSON_file(path):
    file = open(os.path.join(settings.BASE_DIR, path))
    data = file.read()
    file.close()
    return json.loads(data)


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
    
def make_prefix(id):
    if id < 10:
        return f'000{id}'
    if id >= 10 and id < 100:
        return f'00{id}'
    if id >= 100:
        return f'0{id}'
    return str(id)
