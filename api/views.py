from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.db.models import Q, Case, When, Value, IntegerField, Avg
from .models import Place, Review
from .serializers import (
    RegisterSerializer, PlaceSerializer, PlaceDetailSerializer, 
    AddReviewSerializer, ReviewSerializer
)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    return Response({
        "message": "Welcome to the Place Review API",
        "endpoints": {
            "register": "/api/register/",
            "login": "/api/login/",
            "reviews": "/api/reviews/",
            "search": "/api/places/search/",
            "detail": "/api/places/<id>/"
        }
    })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user_id": user.pk,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

class AddReviewView(generics.CreateAPIView):
    serializer_class = AddReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

class PlaceSearchView(generics.ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Place.objects.annotate(average_rating=Avg('reviews__rating'))
        
        query = self.request.query_params.get('query', '')
        min_rating = self.request.query_params.get('min_rating')

        if min_rating:
            try:
                min_r = float(min_rating)
                queryset = queryset.filter(average_rating__gte=min_r)
            except ValueError:
                pass

        if query:
            queryset = queryset.filter(name__icontains=query)
            
            queryset = queryset.annotate(
                is_exact_match=Case(
                    When(name__iexact=query, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('is_exact_match', 'name')
        
        return queryset

class PlaceDetailView(generics.RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        avg_rating = instance.reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        reviews = instance.reviews.select_related('user').all()
        
        current_user_reviews = reviews.filter(user=request.user).order_by('-created_at')
        other_reviews = reviews.exclude(user=request.user).order_by('-created_at')
        
        sorted_reviews = list(current_user_reviews) + list(other_reviews)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['reviews'] = ReviewSerializer(sorted_reviews, many=True).data
        data['average_rating'] = avg_rating
        
        return Response(data)
