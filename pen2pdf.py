import sys
import neosmartpen

# from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
# from reportlab.graphics import renderPDF
# from reportlab.graphics.shapes import Drawing

from reportlab.pdfgen import canvas

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def transition(x,y):
    if x>60 and y<20:
        return True
    else:
        return False


c = canvas.Canvas(sys.argv[2], pagesize=(A4[1],A4[0]), bottomup=0)

pages = neosmartpen.parse_pages(sys.argv[1])
c.setLineCap(1)
c.setAuthor("pen2pdf")
c.setTitle("Notes")
c.setSubject("Notes generated with pen2pdf")


def addPage(canvas, page, strokes):
    S = A4[1]/page['width']

    for s in strokes:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]

        for x,y,p,dt in dots[1:]:
            canvas.setLineWidth(2*p)
            canvas.line(S*x0,S*y0,S*x,S*y)
            x0,y0,p0=x,y,p

    canvas.showPage()


for n,data in enumerate(pages):
    print('Page ', n+1)
    S = A4[0]/data['width']
    strokes = []
    for s in data['strokes']:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]
        if transition(x0,y0):
            addPage(c, data, strokes)
        else:
            strokes.append(s)
    addPage(c, data, strokes)

c.save()

if __name__ == "__main__":
    pass
