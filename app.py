from flask import Flask, jsonify, request, make_response
from jinja2 import Environment, FileSystemLoader
from PyPDF2 import PdfFileReader, PdfWriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

app = Flask(__name__)

@app.route('/pdf', methods=['POST'])
def generate_pdf():
    # Obtener los datos del JSON de la solicitud
    data = request.get_json()

    # Obtener el nombre del archivo y la ruta del template
    filename = data['filename']
    template_path = data['template_path']

    # Obtener las variables del JSON de la solicitud
    variables = data['variables']

    # Cargar el template con Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)

    # Renderizar el template con las variables
    rendered_template = template.render(variables)

    # Crear un objeto PDF vacío
    output_pdf = PdfWriter()

    # Agregar cada página del template renderizado al objeto PDF
    rendered_template_bytes = rendered_template.encode('utf-8')
    rendered_template_pdf = PdfFileReader(data=rendered_template_bytes)
    for page_num in range(rendered_template_pdf.getNumPages()):
        output_pdf.addPage(rendered_template_pdf.getPage(page_num))

    # Crear la respuesta de la API con el archivo PDF
    response = make_response(output_pdf)
    response.headers['Content-Disposition'] = (
        f'attachment; filename={filename}.pdf')
    response.headers['Content-Type'] = 'application/pdf'

    # Obtener la dirección de correo electrónico del destinatario del JSON de la solicitud
    to_email = data['to_email']

    # Crear el mensaje de correo electrónico con el archivo PDF adjunto
    message = MIMEMultipart()
    message['From'] = 'tu_correo_electronico@gmail.com'
    message['To'] = to_email
    message['Subject'] = 'PDF generado desde Flask'

    # Adjuntar el archivo PDF al mensaje
    pdf_attachment = MIMEApplication(response.data, _subtype='pdf')
    pdf_attachment.add_header(
        'Content-Disposition', f'attachment; filename={filename}.pdf')
    message.attach(pdf_attachment)

    # Enviar el mensaje de correo electrónico
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('tu_correo_electronico@gmail.com', 'tu_contraseña')
        smtp.sendmail('tu_correo_electronico@gmail.com', to_email, message.as_string())

    return 'PDF generado y enviado por correo electrónico'

if __name__ == '__main__':
    app.run()