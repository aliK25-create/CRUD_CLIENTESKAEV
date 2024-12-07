from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClienteForm, RegistroForm
from .models import Cliente
# PARA REPORTES
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
import datetime
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q

# Create your views here.
@login_required
def create_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(cliente_list)
    else:
        form = ClienteForm()
    return render(request, 'clienteskaev/cliente_form.html', {'form': form})
        
def cliente_list(request):
    query= request.GET.get("q")
    if query:
        clientes= Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(apellidos__icontains=query) | Q(telefono__icontains=query)
        )
    else:
         clientes = Cliente.objects.all()
    return render(request, 'clienteskaev/cliente_list.html', {'clienteskaev': clientes})

@login_required
def update_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect(cliente_list)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clienteskaev/cliente_form.html', {'form': form, 'cliente': cliente})

@login_required
def delete_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect(cliente_list)
    return render(request, 'clienteskaev/cliente_confirm_delete.html', {'cliente': cliente})

def generar_pdf_cliente(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="clientes.pdf"'
    
    # Configuración para página en formato oficio (horizontal)
    pdf = canvas.Canvas(response, pagesize=landscape(letter))  # Página horizontal tamaño carta
    width, height = landscape(letter)
    pdf.setTitle("Reporte de Cliente")
    
    fecha_generacion = datetime.date.today().strftime("%d-%m-%Y")
    pagina_num = 1

    # Ruta de la imagen
    image_path = os.path.join(settings.BASE_DIR, 'media/clientes_fotos/imageISC.png')

    # Agrega la imagen en la esquina superior izquierda (ajusta x e y según el tamaño de la imagen)
    pdf.drawImage(image_path, width - 90, height - 60, width=55, height=55)  
    
    def pie_pagina(pdf, pagina_num):
        pdf.setFont('Helvetica', 10)
        pdf.drawString(50, 20, f"Fecha de generación: {fecha_generacion}")
        pdf.drawString(width - 110, 20, f"Página núm. {pagina_num}")
    
    # Título del reporte centrado
    pdf.setFont('Helvetica-Bold', 18)
    texto = "Lista de Pacientes"
    ancho_texto = pdf.stringWidth(texto)
    x = (width - ancho_texto) / 2
    pdf.drawString(x, height - 40, texto)
    
    # Encabezado de la tabla con márgenes más amplios
    pdf.setFont('Helvetica-Bold', 14)
    encabezados = ["Nombre", "Apellidos", "Teléfono", "Fecha de Nacimiento"]
    x_inicial = 60
    y = height - 100
    
    # Dibuja encabezados con más espacio entre columnas
    for i, encabezado in enumerate(encabezados):
        pdf.drawString(x_inicial + i * 150, y, encabezado)
    y -= 10
    pdf.line(50, y, width - 50, y)
    y -= 20
    
    # Datos de los clientes
    query= request.GET.get("q")
    if query:
        clientes= Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(apellidos__icontains=query) | Q(telefono__icontains=query)
        )
    else:
         clientes = Cliente.objects.all()
    pdf.setFont('Helvetica', 12)
    for cliente in clientes:
        pdf.drawString(60, y, cliente.nombre)
        pdf.drawString(210, y, cliente.apellidos)
        pdf.drawString(360, y, cliente.telefono)
        
        # Centrar la fecha de nacimiento
        fecha_nac_texto = cliente.fecha_nac.strftime("%d-%m-%Y")
        fecha_nac_width = pdf.stringWidth(fecha_nac_texto, "Helvetica", 12)
        fecha_nac_x = 510 + (150 - fecha_nac_width) / 2  # Centrado dentro de la columna
        pdf.drawString(fecha_nac_x, y, fecha_nac_texto)
        
        y -= 20
        
        if y <= 50:
            pie_pagina(pdf, pagina_num)
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = height - 80
            
            # Redibujar encabezado en nueva página
            for i, encabezado in enumerate(encabezados):
                pdf.drawString(x_inicial + i * 150, y, encabezado)
            y -= 10
            pdf.line(50, y, width - 50, y)
            y -= 20
            
            pagina_num += 1
            
    pie_pagina(pdf, pagina_num)
    pdf.showPage()
    pdf.save()
    
    return response


def logout_view(request):
    logout(request)
    return redirect('login')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registration/register.html', {'form': form})
