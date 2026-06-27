from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import User, Post, Comment, Like
from .serializers import (
    UserSerializer, RegisterSerializer,
    PostSerializer, CommentSerializer,
)


# ─────────────────────────────────────────────────────────
# HELPER: generate JWT token pair for a user
# ─────────────────────────────────────────────────────────
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─────────────────────────────────────────────────────────
# AUTH VIEWS
# POST /api/register/  → create account, return tokens
# POST /api/login/     → authenticate, return tokens
# ─────────────────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {'user': UserSerializer(user, context={'request': request}).data, **tokens},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return Response(
                {'user': UserSerializer(user, context={'request': request}).data, **tokens}
            )
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# ─────────────────────────────────────────────────────────
# USER VIEWS
# GET  /api/users/           → list all users (for discovery)
# GET  /api/users/<id>/      → single profile
# POST /api/users/<id>/follow/    → follow / unfollow toggle
# GET  /api/users/<id>/posts/     → user's posts
# GET  /api/users/me/        → current user's own profile
# ─────────────────────────────────────────────────────────
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnlyModelViewSet gives us list() and retrieve() for free.
    We add custom @action endpoints on top.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Return the logged-in user's own profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk=None):
        """Toggle follow/unfollow for user with given pk."""
        target_user = self.get_object()

        if target_user == request.user:
            return Response({'error': "You can't follow yourself."}, status=400)

        if request.user.following.filter(id=target_user.id).exists():
            request.user.following.remove(target_user)
            return Response({'status': 'unfollowed'})
        else:
            request.user.following.add(target_user)
            return Response({'status': 'followed'})

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Return all posts by a specific user."""
        user = self.get_object()
        posts = Post.objects.filter(author=user)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def feed(self, request):
        """
        Return posts from users the current user follows,
        plus their own posts — sorted newest first.
        """
        following_ids = request.user.following.values_list('id', flat=True)
        posts = Post.objects.filter(
            Q(author__in=following_ids) | Q(author=request.user)
        ).order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────
# POST VIEWS
# GET    /api/posts/          → all posts (explore page)
# POST   /api/posts/          → create post (auth required)
# GET    /api/posts/<id>/     → single post with comments
# DELETE /api/posts/<id>/     → delete own post
# POST   /api/posts/<id>/like/      → toggle like
# POST   /api/posts/<id>/comment/   → add comment
# ─────────────────────────────────────────────────────────
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        """Public can read; must be logged in to create/delete."""
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Automatically assign the logged-in user as author."""
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({'error': 'Not your post.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Toggle like/unlike on a post."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            # Already liked → unlike
            like.delete()
            return Response({'status': 'unliked', 'likes_count': post.likes.count()})

        return Response({'status': 'liked', 'likes_count': post.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to a post."""
        post = self.get_object()
        content = request.data.get('content', '').strip()

        if not content:
            return Response({'error': 'Comment cannot be empty.'}, status=400)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
        )
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=201)