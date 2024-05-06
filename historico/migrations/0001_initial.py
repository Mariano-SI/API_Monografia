# Generated by Django 5.0.3 on 2024-05-06 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now=True, verbose_name='Data')),
                ('usuario', models.CharField(max_length=255, verbose_name='Nome do usuário')),
                ('tipoAcao', models.CharField(max_length=1, verbose_name='Tipo Ação')),
                ('descAcao', models.CharField(max_length=255, verbose_name='Descrição da ação')),
                ('tabela', models.CharField(max_length=255, verbose_name='Tabela alterada')),
                ('idElemento', models.IntegerField(verbose_name='Id do elemento alterado')),
            ],
        ),
    ]
