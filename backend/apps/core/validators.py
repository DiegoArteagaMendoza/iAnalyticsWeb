from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image

IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp", "gif", "ico"]
DOCUMENT_EXTENSIONS = ["pdf", "docx", "xlsx", "pptx", "txt", "csv", "zip"]

validate_image_extension = FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS)
validate_media_extension = FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS + DOCUMENT_EXTENSIONS)


def validate_file_size(uploaded_file):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if uploaded_file.size > max_bytes:
        raise ValidationError(f"El archivo supera el máximo de {settings.MAX_UPLOAD_SIZE_MB} MB.")


def validate_image_content(uploaded_file):
    """Comprueba que el archivo sea realmente una imagen (no solo por la extensión)."""
    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else None
    try:
        with Image.open(uploaded_file) as image:
            image.verify()
    except Exception as error:
        raise ValidationError("El archivo no es una imagen válida.") from error
    finally:
        if position is not None:
            uploaded_file.seek(position)


IMAGE_VALIDATORS = [validate_image_extension, validate_file_size, validate_image_content]
MEDIA_VALIDATORS = [validate_media_extension, validate_file_size]
