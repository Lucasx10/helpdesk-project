from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Chamados, Profile

# Função reutilizável para criar links de ações
def gerar_acoes(obj):
    edit_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
    delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
    return format_html(
        '<a href="{}" title="Editar" style="margin-right: 10px;"><img src="/static/admin/img/icon-changelink.svg" alt="Editar"></a>&nbsp;&nbsp;'
        '<a href="{}" title="Excluir"><img src="/static/admin/img/icon-deletelink.svg" alt="Excluir"></a>',
        edit_url,
        delete_url
    )

@admin.action(description="Concluir chamado")
def action_chamado_concluido(modeladmin, request, queryset):
    for chamado in queryset:
        chamado.status = "Concluído"
        chamado.save()

@admin.register(Chamados)
class ChamadosAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'user', 'setor', 'status', 'created_at', 'acoes')
    list_display_links = ('titulo',)
    search_fields = ('id',)
    list_filter = ('user', 'setor', 'status', 'created_at')
    actions = [action_chamado_concluido]

    def acoes(self, obj):
        return gerar_acoes(obj)

    acoes.short_description = 'Ações'  # Título da coluna

@admin.action(description="Tornar equipe TI")
def action_equipe_ti(modeladmin, request, queryset):
    for profile in queryset:
        profile.equipe_ti = True
        profile.save()
        
@admin.register(Profile)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'user', 'equipe_ti', 'acoes')
    list_filter = ('equipe_ti',)
    search_fields = ('nome',)
    actions = [action_equipe_ti]

    def acoes(self, obj):
        return gerar_acoes(obj)

    acoes.short_description = 'Ações'  # Título da coluna
