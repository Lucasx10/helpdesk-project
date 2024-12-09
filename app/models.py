from django.db import models
from django.contrib.auth.models import User

class StatusChamado(models.TextChoices):
 ABERTO = 'Aberto'
 EM_ANDAMENTO = 'Em Andamento'
 CONCLUIDO = 'Concluído'
 
class Chamados(models.Model):
    titulo = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    status = models.CharField(max_length=25, choices=StatusChamado.choices, default=StatusChamado.ABERTO)
    descricao = models.TextField()
    setor = models.CharField(max_length=50)
    
    # Responsável TI (será preenchido quando um usuário de TI aceitar o chamado)
    responsavel_ti = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True) 

