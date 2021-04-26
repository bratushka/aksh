from django.contrib import admin

from .forms import ActAdminForm, DocumentAdminForm
from .models import Act, Document


class DocumentInline(admin.TabularInline):
    model = Document
    form = DocumentAdminForm
    extra = 0
    readonly_fields = ('last_modified',)


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    form = ActAdminForm
    inlines = (DocumentInline,)

    list_display = (
        '__str__',
        'forwarded',
        'removed_from_source',
        'needs_inspection',
    )
    list_filter = (
        'issuer',
        'act_id',
        'removed_from_source',
        'needs_inspection',
    )
    search_fields = (
        'act_id',
        'title',
    )
