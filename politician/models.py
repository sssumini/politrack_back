from django.db import models
from django.utils import timezone

# Create your models here.
class Community(models.Model):
    community_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=timezone.now()+timezone.timedelta(days=7),editable=False)

class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    community = models.OneToOneField(Community, blank=False, null=False, on_delete=models.CASCADE)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    idea_a = models.TextField(max_length=300)
    idea_b = models.TextField(max_length=300)
    idea_c = models.TextField(max_length=300)
    comment = models.TextField(max_length=300,blank=True)


    PICK_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
    ]
    pick = models.CharField(max_length=10, choices=PICK_CHOICES)