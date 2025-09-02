# game/validators.py
from rest_framework import status
from rest_framework.response import Response

from .models import CharacterClass


def validate_character_attributes(strength, agility, endurance):
    """Validate character attributes"""
    # Define reasonable limits for attributes
    min_value, max_value = 1, 20

    if any(attr < min_value or attr > max_value for attr in [strength, agility, endurance]):
        return Response(
            {'error': f'Attributes must be between {min_value} and {max_value}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Optional: Validate total points if you have a point-buy system
    total_points = strength + agility + endurance
    if total_points < 10 or total_points > 50:  # Adjust these values as needed
        return Response(
            {'error': 'Total attribute points must be between 10 and 50'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def validate_class_id(class_id):
    """Validate that the class ID exists"""
    try:
        CharacterClass.objects.get(id=class_id)
        return None
    except CharacterClass.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
