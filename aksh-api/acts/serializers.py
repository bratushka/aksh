# noinspection PyPep8Naming
import typing as T

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


class ActToForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = (
            'id',
            'issuer',
            'title',
            'link',
            'file_name',
            'files',
        )

    link = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    @staticmethod
    def get_file_name(act: Act) -> str:
        return act.documents.get(order=0).file.name.rsplit('/', 1)[-1]

    @staticmethod
    def get_link(act: Act) -> str:
        return act.documents.get(order=0).url

    @staticmethod
    def get_files(act: Act) -> T.List[str]:
        return [
            document.file.name
            for document in act.documents.all()
        ]
