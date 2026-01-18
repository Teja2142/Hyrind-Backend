from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Job
from .serializers import JobSerializer


class JobListCreate(generics.ListCreateAPIView):
    """
    Job Postings API - List and Create
    GET /api/jobs/ - List all job postings (Public)
    POST /api/jobs/ - Create new job posting (Admin/Recruiter only)
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    @swagger_auto_schema(
        operation_summary="List all job postings",
        operation_description="""Retrieve a list of all active job postings with pagination and search.
        
Returns job information including title, company, location, salary range, requirements, and application deadline.

Query Parameters:
- page: Page number for pagination (default: 1)
- page_size: Items per page (default: 10, max: 100)
- search: Search by job title or company name

Example: GET /api/jobs/?search=software engineer&page=1""",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number for pagination'),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Items per page (max 100)'),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Search by job title or company'),
        ],
        responses={
            200: openapi.Response('List of job postings', JobSerializer(many=True)),
            400: 'Bad request'
        },
        tags=['Jobs']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a new job posting",
        operation_description="""Create a new job posting.
        
Permission: Admin or Recruiter only
Requires authentication and proper permissions.

Required fields: title, company, location, job_type, description
Optional fields: salary_range, requirements, responsibilities, benefits, application_deadline

Example Request:
{
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "job_type": "Full-time",
  "salary_range": "$120,000 - $180,000",
  "description": "We are seeking...",
  "requirements": "5+ years Python, AWS",
  "is_active": true
}""",
        request_body=JobSerializer,
        responses={
            201: openapi.Response('Job created successfully', JobSerializer),
            400: 'Invalid job data - validation errors',
            401: 'Authentication required',
            403: 'Permission denied - only recruiters/admins can create jobs'
        },
        tags=['Jobs']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific job posting"""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    @swagger_auto_schema(
        operation_summary="Get job posting details",
        operation_description="Retrieve complete information about a specific job posting, including description, requirements, salary range, and application deadline.",
        responses={
            200: JobSerializer,
            404: 'Job not found'
        },
        tags=['Jobs']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update job posting",
        operation_description="Update an existing job posting. Only the recruiter who created the job or admins can modify it.",
        request_body=JobSerializer,
        responses={
            200: openapi.Response('Job updated successfully', JobSerializer),
            400: 'Invalid job data',
            403: 'Permission denied',
            404: 'Job not found'
        },
        tags=['Jobs']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update job posting",
        operation_description="Update specific fields of a job posting without replacing the entire record.",
        request_body=JobSerializer,
        responses={
            200: openapi.Response('Job updated successfully', JobSerializer),
            400: 'Invalid data',
            403: 'Permission denied',
            404: 'Job not found'
        },
        tags=['Jobs']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete job posting",
        operation_description="Remove a job posting from the system. Only admins or the job creator can delete.",
        responses={
            204: 'Job deleted successfully',
            403: 'Permission denied',
            404: 'Job not found'
        },
        tags=['Jobs']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
