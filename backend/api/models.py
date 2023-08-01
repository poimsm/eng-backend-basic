from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Status(models.IntegerChoices):
    DELETED = 0, 'Deleted'
    ACTIVE = 1, 'Active'


class Difficulty(models.IntegerChoices):
    EASY = 0, 'Easy'
    MODERATE = 1, 'Moderate'
    COMPLEX = 2, 'Complex'


class QuestionType(models.IntegerChoices):
    QUIZ = 0, 'Quiz question'
    DESCRIBE = 1, 'Describe the picture'
    STORY = 2, 'Build a story'
    SCENARIO = 3, 'Scenario'


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Word(BaseModel):
    id = models.IntegerField(primary_key=True)
    word = models.TextField()
    definition = models.TextField()
    translations = models.JSONField()
    has_info = models.BooleanField(default=False)
    examples = models.JSONField()
    explanations = models.JSONField()
    story = models.JSONField(null=True)
    miniature = models.JSONField()
    difficulty = models.PositiveSmallIntegerField(
        choices=Difficulty.choices,
        default=Difficulty.MODERATE
    )
    objects = models.Manager()

    class Meta:
        db_table = 'words'


class Question(BaseModel):
    id = models.IntegerField(primary_key=True)
    question = models.TextField()
    difficulty = models.PositiveSmallIntegerField(
        null=False,
        choices=Difficulty.choices
    )
    type = models.PositiveSmallIntegerField(
        null=False,
        choices=QuestionType.choices
    )
    image_url = models.TextField()
    scenario = models.JSONField(blank=True, null=True)
    voice_url = models.TextField()
    notes = models.TextField(blank=True, null=True)
    example = models.JSONField(blank=True, null=True)
    words = models.ManyToManyField(Word)
    objects = models.Manager()

    class Meta:
        db_table = 'questions'


class Style(BaseModel):
    background_screen = models.CharField(
        max_length=20, blank=False, null=False)
    background_challenge = models.CharField(
        max_length=20, blank=True, null=True)
    question_opacity = models.DecimalField(
        default=0.4, max_digits=3, decimal_places=2)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    objects = models.Manager()

    class Meta:
        db_table = 'styles'


class Device(BaseModel):
    uuid = models.CharField(max_length=50, blank=False, null=False)
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE
    )
    objects = models.Manager()

    class Meta:
        db_table = 'devices'


class ScreenFlow(BaseModel):
    value = models.CharField(max_length=50, blank=True, null=True)
    time = models.CharField(max_length=50, blank=True, null=True)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE
    )
    objects = models.Manager()

    class Meta:
        db_table = 'screenflow'


class UserHistory(BaseModel):
    total_uses = models.PositiveSmallIntegerField(default=0)
    last_time_used = models.DateTimeField()
    question_id = models.IntegerField(null=False, blank=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    objects = models.Manager()

    class Meta:
        db_table = 'user_history'


class UserProfile(BaseModel):
    verified = models.BooleanField(default=False)
    screen_flow = models.BooleanField(default=False)
    email = models.CharField(max_length=150, blank=False, null=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    objects = models.Manager()

    class Meta:
        db_table = 'user_profiles'
