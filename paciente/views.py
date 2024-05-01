from django.shortcuts import render, redirect
from medico.models import Dados_Medico, Especialidades, DatasAbertas, is_medico
from django.http import HttpResponse
from datetime import datetime
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = Dados_Medico.objects.all()

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'espacialidades': especialidades, 'is_medico': is_medico(request.user)})
    
@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        medico = Dados_Medico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS, 'consulta agendada com sucesso.')
        return redirect('/pacientes/minhas_consultas/')
    

@login_required
def minhas_consultas(request):
    data = request.GET.get("data")
    especialidade = request.GET.get("especialidade")
    minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
    if data:
        minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=data)

    if especialidades:
        minhas_consultas = minhas_consultas.filter(data_aberta__user__dodosmedico__especialidade=especialidades)
    
    especialidades = Especialidades.objects.all()
    return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})

@login_required
def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = Dados_Medico.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'documentos': documentos})
