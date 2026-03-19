import uuid
import boto3
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UploadedFile

# ── File validation constants ─────────────────────────────────────────────────
_ALLOWED_TYPES = {
    'resume': {
        'allowed_mimes': {'application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
        'allowed_extensions': {'pdf', 'doc', 'docx'},
        'max_bytes': 5 * 1024 * 1024,
        'label': 'Resume (PDF / DOC / DOCX, max 5 MB)',
    },
    'credential': {
        'allowed_mimes': {'application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
        'allowed_extensions': {'pdf', 'doc', 'docx'},
        'max_bytes': 5 * 1024 * 1024,
        'label': 'Credential document (PDF / DOC / DOCX, max 5 MB)',
    },
    'offer_letter': {
        'allowed_mimes': {'application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
        'allowed_extensions': {'pdf', 'doc', 'docx'},
        'max_bytes': 5 * 1024 * 1024,
        'label': 'Offer letter (PDF / DOC / DOCX, max 5 MB)',
    },
    'avatar': {
        'allowed_mimes': {'image/jpeg', 'image/png', 'image/webp'},
        'allowed_extensions': {'jpg', 'jpeg', 'png', 'webp'},
        'max_bytes': 2 * 1024 * 1024,
        'label': 'Profile image (JPG / PNG / WEBP, max 2 MB)',
    },
    'document': {
        'allowed_mimes': {
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png',
        },
        'allowed_extensions': {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'},
        'max_bytes': 10 * 1024 * 1024,
        'label': 'Document (PDF / DOC / DOCX / JPG / PNG, max 10 MB)',
    },
}

_DEFAULT_VALIDATION = {
    'allowed_mimes': set(),
    'allowed_extensions': set(),
    'max_bytes': 10 * 1024 * 1024,
    'label': 'File (max 10 MB)',
}


def _validate_upload(file, file_type: str):
    """Returns (is_valid, error_message)."""
    rules = _ALLOWED_TYPES.get(file_type, _DEFAULT_VALIDATION)

    if file.size > rules['max_bytes']:
        limit_mb = rules['max_bytes'] // (1024 * 1024)
        return False, f'File exceeds size limit of {limit_mb} MB for type "{file_type}".'

    ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    if rules['allowed_extensions'] and ext not in rules['allowed_extensions']:
        return False, (
            f'File extension ".{ext}" is not allowed for type "{file_type}". '
            f'Accepted: {", ".join(sorted(rules["allowed_extensions"]))}.'
        )

    content_type = getattr(file, 'content_type', '') or ''
    if rules['allowed_mimes'] and content_type and content_type not in rules['allowed_mimes']:
        return False, (
            f'MIME type "{content_type}" is not allowed for type "{file_type}". '
            f'Accepted: {", ".join(sorted(rules["allowed_mimes"]))}.'
        )

    return True, None


def _get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
        aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
    )


@extend_schema(
    summary='Upload a file to S3/MinIO storage',
    request={'multipart/form-data': {'type': 'object', 'properties': {
        'file': {'type': 'string', 'format': 'binary'},
        'file_type': {
            'type': 'string',
            'enum': ['resume', 'credential', 'offer_letter', 'avatar', 'document'],
            'description': 'Controls allowed extensions/MIME types and size limit',
        },
    }, 'required': ['file']}},
    responses={
        201: OpenApiResponse(description='Uploaded — returns id, bucket_path, original_name'),
        400: OpenApiResponse(description='No file / invalid type / exceeds size limit'),
    },
    tags=['Files'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_file(request):
    file = request.FILES.get('file')
    file_type = request.data.get('file_type', 'document')

    if not file:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    is_valid, error_msg = _validate_upload(file, file_type)
    if not is_valid:
        return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

    ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else 'bin'
    bucket_path = f'{request.user.id}/{file_type}/{uuid.uuid4()}.{ext}'

    s3 = _get_s3_client()
    s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, bucket_path)

    record = UploadedFile.objects.create(
        user=request.user,
        file_type=file_type,
        bucket_path=bucket_path,
        original_name=file.name,
        size_bytes=file.size,
    )

    return Response({
        'id': str(record.id),
        'bucket_path': bucket_path,
        'original_name': file.name,
        'size_bytes': file.size,
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Get a pre-signed download URL for a file',
    responses={
        200: OpenApiResponse(description='Pre-signed URL valid for 1 hour + original filename'),
        404: OpenApiResponse(description='File not found'),
    },
    tags=['Files'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_download_url(request, file_id):
    try:
        record = UploadedFile.objects.get(id=file_id, user=request.user)
    except UploadedFile.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    s3 = _get_s3_client()
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': record.bucket_path},
        ExpiresIn=3600,
    )
    return Response({'url': url, 'original_name': record.original_name})
