from django.core.management.base import BaseCommand
from api.models import (
    UserSentence, ResourceSentence, ShortVideo, InfoCard,
    Collocation, SentenceTypes, SourceTypes, Question, Word,
    QuestionTypes,
)
from users.models import User
from api.helpers import console
from datetime import date
import datetime
from django.utils import timezone


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('      PLAY INIT                 ')
        console.info('--------------------------------')


        # aa = Question.objects.filter(
        #     type=QuestionTypes.DESCRIBE_IMAGE,
        #     has_example=True)
        # print(len(aa))

        # for a in aa:
        #     print(a.question)



        # obj = ShortVideo.objects.get(id=1)
        # print(obj.created)


        # word = Word.objects.get(id=10)
        # question = Question.objects.get(id=1)
        # question.words.remove(word)

        # Question.words.remove(word)




        # question = Question.objects.get(id=49)
        # words = question.words.all()
        
        # for w in words:
        #     print(w.word)

        # print(len(words))
        # print(question.question)






        # questions = Question.objects.all()
        # for q in questions:
        #     q.words.clear()

        # obj = InfoCard.objects.get(id=1)
        # print(obj.created)



        # rr = datetime.datetime.now(tz=timezone.utc)
        # now = timezone.now()
        # naive_utc_dt = datetime.datetime.utcnow()

        # print('rr', rr)
        # print('now', now)
        # print('datetime', datetime.datetime.now())
        # console.info(str(datetime.datetime.now()))
        # print('naive_utc_dt', naive_utc_dt)


        
        # obj = UserSentence.objects.get(id=57)
        # print('Herrrrrrrrre')
        # console.info('Herrrrrrrrre')
        # print(obj.created)
        # console.info(str(obj.created))

        # Collocation(
        #     text="hooola",
        #     source_type=SourceTypes.INFO_CARD,
        #     updated=date.today()
        # ).save()

        # user = User(
        #     id=2,
        #     username='test2',
        #     email='test2@fake.com',
        #     password='123456'
        # )

        # user.save()

        # console.info('Creating user sentences...')

        # UserSentence(
        #     type=0,
        #     origin=0,
        #     sentence='hang out ZZZZZ',
        #     meaning='hang out with friends',
        #     last_time_used=datetime.datetime.now(tz=timezone.utc),
        #     user=user
        # ).save()


        console.info('Migration completed successfully')
