from rest_framework import serializers
from .models import Meesages
import re
from django.core.exceptions import ValidationError
from urllib.request import urlopen
import base64
import uuid
from django.core.files.base import ContentFile

# Serializer for the Meesages model
class MessageSerializer(serializers.ModelSerializer):
    msgFile_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = Meesages
        fields = ["text", "msg_sender", "msg_sender_number", "msgFile", "msgFile_base64"]
        extra_kwargs = {
            "msgFile": {"read_only": True},  # `msgFile` is read-only; we'll populate it from `msgFile_base64`.
            "msgFile_base64": {"write_only": True},
        }

    def validate_msgFile_base64(self, value):
        """
        Decode the base64-encoded file, handle empty string, and return a ContentFile instance.
        """
        if not value:  # If the field is empty string or null, return None
            return None

        try:
            # Check if the base64 string has metadata (e.g., data:image/jpeg;base64,...)
            if ";base64," in value:
                header, base64_data = value.split(";base64,")
                mime_type = header.split(":")[1]  # Extract MIME type
                extension = mime_type.split("/")[-1]
            else:
                base64_data = value
                extension = "txt"  # Default extension if no MIME type is provided

            # Decode the base64 string
            decoded_file = base64.b64decode(base64_data)

            # Generate a unique filename with the correct extension
            file_name = f"{uuid.uuid4()}.{extension}"

            return ContentFile(decoded_file, name=file_name)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 file format: {str(e)}")

    def create(self, validated_data):
        """
        Create the Meesages instance and handle base64 file.
        """
        base64_file = validated_data.pop("msgFile_base64", None)
        instance = Meesages.objects.create(**validated_data)

        # Set msgFile to empty if no valid base64 file is provided
        if base64_file:
            instance.msgFile = base64_file
        else:
            instance.msgFile = ''  # Explicitly set to empty

        instance.save()
        return instance