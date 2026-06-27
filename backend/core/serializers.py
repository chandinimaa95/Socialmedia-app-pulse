from rest_framework import serializers
from .models import User, Post, Comment, Like


# ─────────────────────────────────────────────
# SERIALIZERS convert Django model instances ↔ JSON.
# They also handle validation on incoming data.
# ─────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    Public profile info — never expose password hashes.
    followers_count / following_count are computed properties
    (defined as methods on the model), so we use SerializerMethodField.
    """
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()   # "does the requester follow this user?"

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar',
            'website', 'created_at',
            'followers_count', 'following_count', 'is_following',
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        # `context['request']` is passed in by the ViewSet automatically
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False


class RegisterSerializer(serializers.ModelSerializer):
    """Used only for /api/register/ — accepts plain-text password and hashes it."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # create_user() automatically hashes the password
        return User.objects.create_user(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)     # nested: show full author object

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()       # "did the requester like this post?"

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'image',
            'created_at', 'updated_at',
            'likes_count', 'is_liked', 'comments',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False