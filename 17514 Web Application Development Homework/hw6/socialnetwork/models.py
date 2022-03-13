from django.db import models
from django.contrib.auth.models import User

# a data model for the enhanced profile called Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.CharField(max_length=200, default=None)    
    picture = models.FileField(blank=True)    
    following = models.ManyToManyField(User, related_name="followers")
    content_type = models.CharField(max_length=50)

# a data model for posts 
class Post(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    text = models.CharField(max_length=200)    
    creation_time = models.DateTimeField()        
    
    def __str__(self):
        return 'id=' + str(self.id) + ',text="' + self.text + '"'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    # user = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.CharField(max_length=200)
    creation_time = models.DateTimeField()        
    
    def __str__(self):
        return 'id=' + str(self.id) + ', text="' + self.text + '"'
    