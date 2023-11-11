from django.db import models
from django.utils import timezone
from user.models import User

# Create your models here.
class Community(models.Model):
    community_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=timezone.now()+timezone.timedelta(days=7),editable=False)


class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, related_name='board', blank=False, null=False, on_delete=models.CASCADE)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    idea_a = models.TextField(max_length=300,blank=True)
    idea_b = models.TextField(max_length=300,blank=True)
    idea_c = models.TextField(max_length=300,blank=True)
    idea_a_des = models.TextField(max_length=300,blank=True)
    idea_b_des = models.TextField(max_length=300,blank=True)
    idea_c_des = models.TextField(max_length=300,blank=True)

    pick_title = models.TextField(max_length=300,blank=True)
    PICK_CHOICES = [
        ('option1', 'Option1'),
        ('option2', 'Option2'),
        ('option3', 'Option3'),
    ]
    pick = models.CharField(max_length=10, choices=PICK_CHOICES,blank=True)
    


class Opinion(models.Model):
    opinion_id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, related_name='opinion', blank=False, null=False, on_delete=models.CASCADE, default=3)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    comment = models.TextField(max_length=300,blank=False)


class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100,blank=True)
    pick_title = models.TextField(max_length=300,blank=True)
    PICK_CHOICES = [
        ('option1', 'Option1'),
        ('option2', 'Option2'),
    ]
    pick = models.CharField(max_length=10, choices=PICK_CHOICES)

    ANSWER_CHOICES = [
        ('option1', 'Option1'),
        ('option2', 'Option2'),
    ]
    answer = models.CharField(max_length=10, choices=ANSWER_CHOICES)
    answer_des = models.TextField(max_length=300,blank=True)