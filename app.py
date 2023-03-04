from flask import Flask, request, send_file
from flask_mail import Mail, Message
from flask import render_template
import pdfkit
from decimal import Decimal

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'storebabyprince@outlook.com'
app.config['MAIL_PASSWORD'] = 'Janina123@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    numero_factura = data['numero_factura']
    fecha_emision = data['fecha_emision']
    nombre_cliente = data['nombre_cliente']
    email_cliente = data['email_cliente']
    telefono_cliente = data['telefono_cliente']
    direccion_cliente = data['direccion_cliente']
    nombre_admin = data['nombre_admin']
    email_admin = data['email_admin']
    telefono_admin = data['telefono_admin']
    nombre_articulo1 = data['nombre_articulo1']
    descripcion_articulo1 = data['descripcion_articulo1']
    cant1 = Decimal(data['cant1'])
    precio_unit = Decimal(data['precio_unit'])
    precio_total = Decimal(data['precio_total'])
    subtotal = Decimal(data['subtotal'])
    impuestos = Decimal(data['impuestos'])
    total_pagar = Decimal(data['total_pagar'])

    # Renderizar el template HTML con los datos del usuario
    html = render_template('form.html', numero_factura=numero_factura, fecha_emision=fecha_emision,
                           nombre_cliente=nombre_cliente, email_cliente=email_cliente,
                           telefono_cliente=telefono_cliente, direccion_cliente=direccion_cliente,
                           nombre_admin=nombre_admin, email_admin=email_admin, telefono_admin=telefono_admin,
                           nombre_articulo1=nombre_articulo1, descripcion_articulo1=descripcion_articulo1,
                           cant1="${:.2f}".format(cant1), precio_unit="${:.2f}".format(precio_unit),
                           precio_total="${:.2f}".format(precio_total),
                           subtotal="${:.2f}".format(subtotal),
                           impuestos="${:.2f}".format(impuestos),
                           total_pagar="${:.2f}".format(total_pagar))

    config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    # Genera el archivo PDF utilizando pdfkit y wkhtmltopdf
    pdf_file = 'invoice.pdf'
    pdfkit.from_string(html, pdf_file, configuration=config)

    # Mandar el correo electrónico con el archivo PDF adjunto
    msg = Message('PDF generado', sender='storebabyprince@outlook.com', recipients=[email_cliente])
    with app.open_resource(pdf_file) as fp:
        msg.attach(pdf_file, "application/pdf", fp.read())
    mail.send(msg)

    # Enviar el archivo PDF generado al cliente
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
