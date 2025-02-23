"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'user']
        read_only_fields = ['id', 'user']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'user']
        read_only_fields = ['id', 'user']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
            ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags_data, recipe):
        """Handle getting or creating tags."""
        auth_user = self.context['request'].user
        for tag in tags_data:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        """Handle getting or creating ingredients."""
        auth_user = self.context['request'].user
        for ingredient in ingredients_data:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new recipe."""
        tags_data = validated_data.pop('tags', [])
        Ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)
        self._get_or_create_ingredients(Ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe."""
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)

        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        read_only_fields = RecipeSerializer.Meta.read_only_fields
