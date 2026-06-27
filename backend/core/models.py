from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ─────────────────────────────────────────────
# 1. CUSTOM USER MODEL
# Extends Django's built-in user to add:
#   - avatar / bio / website
#   - follower relationships (many-to-many self-referential)
# ─────────────────────────────────────────────
class User(AbstractUser):
    bio = models.TextField(blank=True, max_length=300)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Self-referential M2M: a user can follow many users
    # "through" is not needed here; Django handles the join table
    following = models.ManyToManyField(
        'self',
        symmetrical=False,          # following A doesn't mean A follows back
        related_name='followers',   # user.followers gives who follows this user
        blank=True,
    )

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def __str__(self):
        return self.username


# ─────────────────────────────────────────────
# 2. POST MODEL
# Each post belongs to a User (author).
# Supports image attachments and tracks creation time.
# ─────────────────────────────────────────────
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,   # delete posts when user is deleted
        related_name='posts',
    )
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # newest first by default

    def likes_count(self):
        return self.likes.count()

    def comments_count(self):
        return self.comments.count()

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


# ─────────────────────────────────────────────
# 3. COMMENT MODEL
# Each comment belongs to both a Post and a User.
# ─────────────────────────────────────────────
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']   # oldest first for comment threads

    def __str__(self):
        return f"{self.author.username} on post {self.post.id}"


# ─────────────────────────────────────────────
# 4. LIKE MODEL
# Tracks who liked which post.
# unique_together prevents duplicate likes.
# ─────────────────────────────────────────────
class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')  # one like per user per post

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"