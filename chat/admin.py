from django.contrib import admin
from .models import ChatRoom, ChatRoomParticipant, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display  = ('room_identifier', 'candidate', 'is_active', 'created_at')
    search_fields = ('room_identifier', 'candidate__user__email')
    raw_id_fields = ('candidate',)


@admin.register(ChatRoomParticipant)
class ChatRoomParticipantAdmin(admin.ModelAdmin):
    list_display  = ('user', 'room', 'role_label', 'is_active', 'added_at')
    list_filter   = ('is_active', 'role_label')
    search_fields = ('user__email', 'room__room_identifier')
    raw_id_fields = ('room', 'user', 'added_by')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ('room', 'sender', 'sender_role', 'is_system_message', 'sent_at')
    list_filter   = ('sender_role', 'is_system_message')
    search_fields = ('room__room_identifier', 'sender__email', 'message_text')
    raw_id_fields = ('room', 'sender')
