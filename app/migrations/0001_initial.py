# Generated by Django 5.1.4 on 2024-12-09 14:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chamados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('Aberto', 'Aberto'), ('Em Andamento', 'Em Andamento'), ('Concluído', 'Concluido')], default='Aberto', max_length=25)),
                ('descricao', models.TextField()),
                ('setor', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('responsavel_ti', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chamados_atendidos', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chamados_abertos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
