#!/usr/bin/env python3
import sys
import neosmartpen
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import argparse
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


parser = argparse.ArgumentParser(description='Convert Neo SmatPen zip file to PDF.')
parser.add_argument('input',  help='Input zip file')
parser.add_argument('output', help='Output PDF file')
parser.add_argument('-t', nargs=4, default=(60,0,200,10), metavar=('x1','y1','x2','y2'), type=int, help='Transition trigger region')

args = parser.parse_args()

TRANSITION_REGION = args.t

def transition(x,y):
    if TRANSITION_REGION[0]<x<TRANSITION_REGION[2] and \
       TRANSITION_REGION[1]<y<TRANSITION_REGION[3]:
        return True
    else:
        return False

c = canvas.Canvas(args.output, pagesize=(A4[0],A4[1]), bottomup=0)

pages = neosmartpen.parse_pages(args.input)
c.setLineCap(1)
c.setAuthor("pen2pdf")
c.setTitle("Notes")
c.setSubject("Notes generated with pen2pdf")


def addPage(canvas, page, strokes):
    S = A4[0]/page['width']

    for s in strokes:
        dots = s['dots']
        x0,y0,p0,dt0 = dots[0]

        for x,y,p,dt in dots[1:]:
            canvas.setLineWidth((s['thickness']+2)*p)
            col = s['color']
            canvas.setStrokeColorRGB(col[1]/255,col[2]/255,col[3]/255)
            canvas.line(S*x0,S*y0,S*x,S*y)
            x0,y0,p0=x,y,p

    canvas.showPage()


for n,data in enumerate(pages):
    logging.info('Generating Page: %d', n+1)
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

