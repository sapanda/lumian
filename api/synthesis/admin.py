from django.contrib import admin
from .models import ProcessedTranscript


class ProcessedTranscriptAdmin(admin.ModelAdmin):
    readonly_fields = ['indexed_display']

    def indexed_display(self, obj):
        return obj.indexed
    indexed_display.short_description = 'Indexed'

    list_display = ('__str__', 'indexed_display')


admin.site.register(ProcessedTranscript, ProcessedTranscriptAdmin)
