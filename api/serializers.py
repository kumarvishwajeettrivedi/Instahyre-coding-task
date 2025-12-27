from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Place, Review

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'phone_number')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('name', 'phone_number', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = Review
        fields = ('id', 'user_name', 'rating', 'text', 'created_at')

class PlaceSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Place
        fields = ('id', 'name', 'address', 'average_rating')

class PlaceDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Place
        fields = ('id', 'name', 'address', 'average_rating', 'reviews')

class AddReviewSerializer(serializers.Serializer):
    place_name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField()

    def create(self, validated_data):
        user = self.context['request'].user
        place_name = validated_data['place_name']
        address = validated_data['address']

        with transaction.atomic():
            place, created = Place.objects.get_or_create(
                name=place_name,
                address=address
            )
            
            review = Review.objects.create(
                place=place,
                user=user,
                rating=validated_data['rating'],
                text=validated_data['review_text']
            )
        return review
