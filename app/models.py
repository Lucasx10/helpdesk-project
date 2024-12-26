from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    equipe_ti = models.BooleanField(default=False)
    nome = models.CharField(max_length=100, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome
    
class StatusChamado(models.TextChoices):
 ABERTO = 'Aberto'
 EM_ANDAMENTO = 'Em Andamento'
 PENDENTE = 'Pendente'
 CONCLUIDO = 'Concluído'
 
class Chamados(models.Model):
    titulo = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chamados_abertos')
    status = models.CharField(max_length=25, choices=StatusChamado.choices, default=StatusChamado.ABERTO)
    descricao = models.TextField()
    tipo_equipamento = models.CharField(max_length=50, null=True, blank=True)
    setor = models.CharField(max_length=50)
    
    # Responsável TI (será preenchido quando um usuário de TI aceitar o chamado)
    responsavel_ti = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chamados_atendidos')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True) 
    
    def __str__(self):
        return self.titulo

class Comentarios(models.Model):
    chamado = models.ForeignKey(Chamados, related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.chamado