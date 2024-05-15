from django.shortcuts import render, redirect, get_object_or_404
from .models import Documentos
from . forms import DocumentosForm
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.urls import reverse
from documentos.functions import handle_uploaded_file
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import views
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .serializer import DocumentosSerializer
from django.shortcuts import render
from .models import Documentos
import os
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from historico.models import Historico
from historico.views import adicionar_historico, remover_historico, atualiza_historico
from django.contrib.auth.decorators import login_required
import rest_framework.permissions as permissions

def view_pdf(request, filename):
    pdf_path = os.path.join('documentos/pdfs', filename)
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    else:
        return HttpResponseNotFound('PDF not found')
    
def listar_documentos(request):
    documentos = Documentos.objects.all()
    return render(request, 'documentosDataTable.html', {'documentos': documentos})

@login_required(login_url="/auth/login/")
def adicionar_documento(request):
    form = DocumentosForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = DocumentosForm(request.POST, request.FILES)
        if form.is_valid(): 
            handle_uploaded_file(request.FILES['arquivo'])
            model_instace = form.save(commit=False)
            model_instace.save()
            model_instace.autor.set(form.cleaned_data['autor'])
            model_instace.orientador.set(form.cleaned_data['orientador'])
            model_instace.coorientador.set(form.cleaned_data['coorientador'])
            # adicionando ao historico
            adicionar_historico(request.user.username, 'Documento', model_instace.id) 
            
            documentos = Documentos.objects.all()
            return redirect('/documentos', {'Documentos': documentos})
    else:
        form = DocumentosForm()
        return render(request, 'adicionar_documento.html', {'form': form})
        
    return render(request, 'adicionar_documento.html', {'form': form, 'editar_documento': False})

@login_required(login_url="/auth/login/")
def atualizar_documento(request, documento_id=None):  # Aceita o parâmetro documento_id
    # Se o documento_id for fornecido, recuperar o documento correspondente
    documento = None
    if documento_id is not None:
        documento = Documentos.objects.get(pk=documento_id)

    if request.method == 'POST':
        form = DocumentosForm(request.POST, request.FILES, instance=documento)  # Passa a instância do documento para o formulário
        if form.is_valid(): 
            atualiza_historico(request.user.username, 'Documento', form, Documentos.objects.get(pk=documento_id))
            form.save()
            
            documentos = Documentos.objects.all()
            return redirect('/documentos', {'Documentos': documentos})
    else:
        form = DocumentosForm(instance=documento)  # Passa a instância do documento para o formulário

    documentos = Documentos.objects.all()
    return render(request, 'adicionar_documento.html', {'form': form, 'documentos': documentos, 'documento_id': documento_id, 'editar_documento': True})

@login_required(login_url="/auth/login/")
def excluir_documento(request, documento_id):
    documento = get_object_or_404(Documentos, id=documento_id)
    documento.delete()
    remover_historico(request.user.username, 'Documentos', documento_id)

    documentos = Documentos.objects.all()
    return redirect('/documentos', {'Documentos': documentos})

@swagger_auto_schema(method='get', responses={200: openapi.Response("List of Documentos", DocumentosSerializer(many=True))}, tags=['Documentos'])
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def listar_documentosAPI(request):
    """
    Listar todos os documentos.
    """
    if request.method == 'GET':
        documentos = Documentos.objects.all()
        serializer = DocumentosSerializer(documentos, many=True)
        return Response(serializer.data)

@swagger_auto_schema(methods=['post'], responses={200:openapi.Response("Documento", DocumentosSerializer())}, request_body=DocumentosSerializer, tags=["Documentos"])
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def adicionar_documentoAPI(request):
    serializer = DocumentosSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='get', responses={200:openapi.Response("Documento", DocumentosSerializer())}, tags=["Documentos"])
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def detalhe_documento(request,pk):
    try:
        documento = Documentos.objects.get(pk=pk)
    except Documentos.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = DocumentosSerializer(documento)
    return Response(serializer.data)

@swagger_auto_schema(methods=['delete','put','patch'], responses={200:openapi.Response("Documento", DocumentosSerializer())}, tags=["Documentos"])
@api_view(['DELETE', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAdminUser])
def atualiza_documento(request, pk):
    try:
        documento = Documentos.objects.get(pk=pk)
    except Documentos.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        documento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method in ['PUT', 'PATCH']:
        serializer = DocumentosSerializer(documento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class FileUploadView(views.APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(manual_parameters=[openapi.Parameter(name="file",in_=openapi.IN_FORM,type=openapi.TYPE_FILE,required=True,description="Document")], responses={200:openapi.Response("Documento", DocumentosSerializer())}, tags=["Documentos"])
    @permission_classes([permissions.IsAuthenticated])
    def put(self, request, pk, format=None):
        file_obj = request.data['file']
        documento = Documentos.objects.get(pk = pk)
        if file_obj:
            documento.arquivo = file_obj
            documento.save()
            return Response(status=204)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)