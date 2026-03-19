"""
Internal Group Chat System — v4 spec Section 6.
One chat room per candidate. All assigned team members participate.
Personal contact details must NEVER appear in chat metadata.
"""
import uuid
from django.db import models
from django.conf import settings
from candidates.models import Candidate


class ChatRoom(models.Model):
    """One group chat room per candidate profile."""
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate        = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='chat_room')
    room_identifier  = models.CharField(max_length=255, unique=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_rooms'

    def save(self, *args, **kwargs):
        if not self.room_identifier:
            self.room_identifier = f'candidate_{self.candidate_id}_group_chat'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.room_identifier


class ChatRoomParticipant(models.Model):
    """Participants — auto-updated when recruiter assignments change."""
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room       = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participants')
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_participations'
    )
    role_label = models.CharField(max_length=30)     # display role label, NOT personal contact
    is_active  = models.BooleanField(default=True)   # False = removed, history preserved
    added_at   = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(blank=True, null=True)
    added_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='chat_additions',
    )

    class Meta:
        db_table     = 'chat_room_participants'
        unique_together = [('room', 'user')]

    def __str__(self):
        return f'{self.user.email} in {self.room.room_identifier}'


class ChatMessage(models.Model):
    """Individual message — soft-deletable, editable."""
    SENDER_ROLE_CHOICES = [
        ('candidate',    'Candidate'),
        ('recruiter',    'Recruiter'),
        ('team_lead',    'Team Lead'),
        ('team_manager', 'Team Manager'),
        ('admin',        'Admin'),
    ]

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room             = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages'
    )
    sender_role      = models.CharField(max_length=20, choices=SENDER_ROLE_CHOICES)
    message_text     = models.TextField(max_length=2000)
    attachment_url   = models.URLField(blank=True, null=True)
    is_system_message = models.BooleanField(default=False)
    sent_at          = models.DateTimeField(auto_now_add=True)
    edited_at        = models.DateTimeField(blank=True, null=True)
    deleted_at       = models.DateTimeField(blank=True, null=True)  # soft delete

    class Meta:
        db_table = 'chat_messages'
        ordering = ['sent_at']

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        sender = self.sender.email if self.sender else 'system'
        return f'[{self.room.room_identifier}] {sender}: {self.message_text[:50]}'
