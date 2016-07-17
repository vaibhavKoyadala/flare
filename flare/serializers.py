from rest_framework import serializers
import models
class TextMessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=30)
    timestamp = serializers.DateTimeField()
    joker_name = serializers.CharField(max_length=30, write_only=True)

    def create(self, validated_data):
        print 'Trying to create TextMessageSerializer'
        assert 'joker' in validated_data, (
            "A joker instance must be provided to "+
            "create a TextMessage."
        )
        return models.TextMessage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError("Update() in TextMessageSerializer is not yet implemented.")

class FlareSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Flare
        fields = ['name', 'created']

class JokerSerializer(serializers.ModelSerializer):
    flare = FlareSerializer()
    class Meta:
        model = models.Joker
        fields = ['name', 'flare', 'last_active', 'joined_on']
#
# class JokerSerializer(serializers.Serializer):
#     class Meta:
#         model = models.Joker
#         fields = ['name', 'is_active', 'joined_on']

