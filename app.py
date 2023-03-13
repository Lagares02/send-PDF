from flask import Flask, render_template, request
from xhtml2pdf import pisa
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

app = Flask(__name__)

@app.route('/enviar_pdf', methods=['POST'])
def enviar_pdf():
    # Obtener datos del objeto JSON enviado en la solicitud POST
    data = request.get_json()
    numero_factura = data.get('numero_factura')
    fecha_emision = data.get('fecha_emision')
    nombre_cliente = data.get('nombre_cliente')
    email_cliente = data.get('email_cliente')
    telefono_cliente = data.get('telefono_cliente')
    direccion_cliente = data.get('direccion_cliente')
    nombre_admin = data.get('nombre_admin')
    email_admin = data.get('email_admin')
    telefono_admin = data.get('telefono_admin')
    nombre_articulo = data.get('nombre_articulo')
    descripcion_articulo = data.get('descripcion_articulo')
    cant_str = data.get('cant')
    precio_unit_str = data.get('precio_unit')
    precio_total_str = data.get('precio_total')
    subtotal_str = data.get('subtotal')
    impuestos_str = data.get('impuestos')
    total_pagar_str = data.get('total_pagar')

    # convertir los valores a tipo float
    cant = float(cant_str) if cant_str is not None else None
    precio_unit = float(precio_unit_str) if precio_unit_str is not None else None
    precio_total = float(precio_total_str) if precio_total_str is not None else None
    subtotal = float(subtotal_str) if subtotal_str is not None else None
    impuestos = float(impuestos_str) if impuestos_str is not None else None
    total_pagar = float(total_pagar_str) if total_pagar_str is not None else None

    # Renderizar plantilla HTML con los datos del formulario
    html = render_template('form.html', 
                           numero_factura=numero_factura,
                           fecha_emision=fecha_emision,
                           nombre_cliente=nombre_cliente,
                           email_cliente=email_cliente,
                           telefono_cliente=telefono_cliente,
                           direccion_cliente=direccion_cliente,
                           nombre_admin=nombre_admin,
                           email_admin=email_admin,
                           telefono_admin=telefono_admin,
                           nombre_articulo=nombre_articulo,
                           descripcion_articulo=descripcion_articulo,
                           cant=cant,
                           precio_unit=precio_unit,
                           precio_total=precio_total,
                           subtotal=subtotal,
                           impuestos=impuestos,
                           total_pagar=total_pagar)

    # Crear archivo PDF a partir
    pdf = None
    try:
        pdf = pisa.CreatePDF(html)
    except Exception as e:
        return "Error creando el documento PDF"

    # Crear mensaje de correo electrónico con archivo adjunto
    msg = MIMEMultipart()
    msg['From'] = os.environ.get('EMAIL_USERNAME')
    msg['To'] = email_cliente
    msg['Subject'] = 'Factura'

    if nombre_cliente is not None:
        body = "Hola " + nombre_cliente + ",\n\n" + "Adjunto encontrará su factura correspondiente a la compra realizada."
    else:
        body = "Hola,\n\nAdjunto encontrará su factura correspondiente a la compra realizada."

    msg.attach(MIMEText(body, 'plain'))

    filename = "factura.pdf"
    part = MIMEApplication(pdf.dest.getvalue(), _subtype = 'pdf')
    part.add_header('content-disposition', 'attachment', filename=filename)
    msg.attach(part)

    # Enviar correo electrónico con archivo adjunto
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(os.environ.get('EMAIL_USERNAME'), os.environ.get('EMAIL_PASSWORD'))
    server.sendmail(os.environ.get('EMAIL_USERNAME'), email_cliente, msg.as_string())
    server.quit()
    return "documento PDF enviado con éxito"