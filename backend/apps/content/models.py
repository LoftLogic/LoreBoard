"""
Content models for LoreBoard
Handles story content, chapters, and writing sessions
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
import uuid


class Content(models.Model):
    """
    Main content model for storing writing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    # Relationships
    entities = models.ManyToManyField(
        'entities.Entity', 
        related_name='contents',
        blank=True
    )
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='children'
    )
    
    # Metadata
    metadata = models.JSONField(default=dict)
    word_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_autosave = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def calculate_word_count(self):
        """Calculate and update word count"""
        self.word_count = len(self.body.split())
        self.save(update_fields=['word_count'])
        return self.word_count


class ContentVersion(models.Model):
    """
    Version control for content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    # Change tracking
    change_summary = models.TextField(blank=True)
    word_count_delta = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['content', 'version_number']
        ordering = ['content', '-version_number']
    
    def __str__(self):
        return f"{self.content.title} - v{self.version_number}"


class AutoFillSlot(models.Model):
    """
    Tracks auto-fill slots in content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='autofill_slots')
    
    # Position in text
    position_start = models.IntegerField()
    position_end = models.IntegerField()
    
    # Context for LLM
    context_before = models.TextField()
    context_after = models.TextField()
    
    # Suggestions and selection
    suggestions = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True
    )
    selected_suggestion = models.CharField(max_length=255, blank=True)
    custom_text = models.CharField(max_length=255, blank=True)
    
    # Status
    is_filled = models.BooleanField(default=False)
    filled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['content', 'position_start']
    
    def __str__(self):
        return f"Slot at {self.position_start} in {self.content.title}"


class WritingSession(models.Model):
    """
    Track writing sessions for analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writing_sessions')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='writing_sessions')
    
    # Session data
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    
    # Productivity metrics
    words_written = models.IntegerField(default=0)
    words_deleted = models.IntegerField(default=0)
    autofills_used = models.IntegerField(default=0)
    entities_referenced = models.IntegerField(default=0)
    
    # Session metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['content', '-start_time']),
        ]
    
    def __str__(self):
        return f"Session for {self.content.title} on {self.start_time}"
    
    def calculate_duration(self):
        """Calculate session duration"""
        if self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=['duration_seconds'])
        return self.duration_seconds


class ContentTag(models.Model):
    """
    Tags for organizing content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#a855f7')  # Hex color
    
    contents = models.ManyToManyField(Content, related_name='tags', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ContentTemplate(models.Model):
    """
    Reusable templates for content structure
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_templates')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Template structure
    structure = models.JSONField(default=dict)
    default_entities = models.ManyToManyField('entities.Entity', blank=True)
    
    # Usage tracking
    times_used = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-times_used', 'name']
    
    def __str__(self):
        return self.name
