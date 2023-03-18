import json
from flask import Flask, render_template
from xhtml2pdf import pisa
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

app = Flask(__name__)

@app.route('/enviar_pdf/<int:cliente_id>/<int:numero_factura>', methods=['GET'])
def enviar_pdf(cliente_id, numero_factura):
    # Cargar datos del archivo JSON
    with open('media/data.json') as f:
        data = json.load(f)

    # Buscar factura en el archivo JSON
    factura = None
    for f in data['facturas']:
        if f['cliente_id'] == cliente_id and f['numero_factura'] == numero_factura:
            factura = f
            break

    # Verificar si se encontró la factura
    if factura is None:
        return "No se encontró la factura especificada"

    # Obtener datos de la factura
    fecha_emision = factura['fecha_emision']
    nombre_cliente = factura['nombre_cliente']
    email_cliente = factura['email_cliente']
    telefono_cliente = factura['telefono_cliente']
    direccion_cliente = factura['direccion_cliente']
    articulos = factura.get('articulos', [])
    subtotal = factura["subtotal"]
    impuestos = factura["impuestos"]
    total_pagar = factura["total_pagar"]

    # Renderizar plantilla HTML con los datos del formulario
    html = render_template('form.html', 
                           numero_factura=numero_factura,
                           fecha_emision=fecha_emision,
                           nombre_cliente=nombre_cliente,
                           email_cliente=email_cliente,
                           telefono_cliente=telefono_cliente,
                           direccion_cliente=direccion_cliente,
                           articulos=articulos,
                           subtotal=subtotal,
                           impuestos=impuestos,
                           total_pagar=total_pagar)

    # convertir los valores a tipo float
    subtotal = float(subtotal) if subtotal is not None else None
    impuestos = float(impuestos) if impuestos is not None else None
    total_pagar = float(total_pagar) if total_pagar is not None else None

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