from rest_framework import serializers

from .models import Act, Document


class InlineDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('order', 'url', 'last_modified')


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'

    documents = InlineDocumentSerializer(many=True)

    def create(self, validated_data):
        documents = validated_data.pop('documents')
        act = Act.objects.create(**validated_data)
        for document in documents:
            Document.objects.create(act=act, **document)

        return act


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
