from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


def generar_factura_pdf(venta_id, fecha, productos, total):

    carpeta = "facturas"

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    nombre_archivo = f"{carpeta}/factura_{venta_id}.pdf"

    pdf = canvas.Canvas(nombre_archivo, pagesize=letter)

    y = 750

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, "FACTURA DE VENTA")

    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Factura No: {venta_id}")

    y -= 20
    pdf.drawString(50, y, f"Fecha: {fecha}")

    y -= 40

    pdf.drawString(50, y, "Código")
    pdf.drawString(120, y, "Producto")
    pdf.drawString(280, y, "Cant.")
    pdf.drawString(350, y, "Precio")
    pdf.drawString(450, y, "Subtotal")

    y -= 20

    pdf.line(50, y, 550, y)

    y -= 20

    for item in productos:

        pdf.drawString(50, y, str(item["codigo"]))
        pdf.drawString(120, y, item["nombre"])
        pdf.drawString(280, y, str(item["cantidad_carrito"]))
        pdf.drawString(350, y, f"${item['precio']:.2f}")
        pdf.drawString(450, y, f"${item['precio_total']:.2f}")

        y -= 20

    y -= 20

    pdf.line(50, y, 550, y)

    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(350, y, f"TOTAL: ${total:.2f}")

    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(180, y, "Gracias por su compra")

    pdf.save()

    return nombre_archivo
