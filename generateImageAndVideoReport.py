# Dependencies
# pip install python-docx 
# pip install pillow
# pip install opencv-python
# pip install pyexiftool

import os
import cv2
import exiftool

# Check config_file_example for more info
from config_file import TMP_PATH, to_remove

from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING

from pathlib import Path

from PIL import Image
from PIL import ExifTags

from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

def insertHR(paragraph):
    p = paragraph._p  # p is the <w:p> XML element
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    pPr.insert_element_before(pBdr,
        'w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap',
        'w:overflowPunct', 'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN',
        'w:bidi', 'w:adjustRightInd', 'w:snapToGrid', 'w:spacing', 'w:ind',
        'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc',
        'w:textDirection', 'w:textAlignment', 'w:textboxTightWrap',
        'w:outlineLvl', 'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr',
        'w:pPrChange'
    )
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    pBdr.append(bottom)


# Función para filtrar los directorios
def filtrar_directorios(nombreFichero):
    for directorio in to_remove:
        if directorio in nombreFichero:
            print('FILTRADO!')
            return True
    return False

# Función para convertir las imágenes a JPG y ajustar la escala
def prepare_image(image_path):
    path = Path(image_path)
    if path.suffix.lower() in {'.jpg', '.png', '.jfif', '.exif', '.gif', '.tiff', '.bmp'}:
        jpg_image_path = f'{TMP_PATH}{path.stem}_result.jpg'
        img = Image.open(image_path)
        ratio = min (640 / img.width, 480 / img.height)
        img.resize((int(ratio * float(img.width)), int(ratio * float(img.height))), 0).convert('RGB').save(jpg_image_path)
        return jpg_image_path
    return image_path

def metadatos_imagen(image_path):
    path = Path(image_path)
    exif = {}
    if path.suffix.lower() in {'.jpg', '.png', '.jfif', '.exif', '.gif', '.tiff', '.bmp'}:
        img = Image.open(image_path)
        img_exif = img._getexif()
        if img_exif is None:
            exif[0] = 'None'
        else: 
            for k, v in img_exif.items():
                tag = ExifTags.TAGS.get(k)
                exif[tag] = str(v)
            
            return exif
    return exif


def inserta_metadatos(doc, exif):

    paragraph = doc.add_paragraph()
    paragraph.style = 'Normal'
    run = paragraph.add_run('Metadatos: ')
    run.font.size = Pt(16)
    run.font.bold = True


    paragraph = doc.add_paragraph()
    paragraph.space_after = Pt(0)
    paragraph.space_before = Pt(0)

    for key in exif:
        run = paragraph.add_run(str(key))
        run.font.bold = True
        run.font.size = Pt(8)
        try:
            run = paragraph.add_run(": " + exif[key] + '\n')
        except Exception as e:
            run = paragraph.add_run(": ???" + '\n')
        run.font.bold = False
        run.font.size = Pt(8)
    return

    paragraph = doc.add_paragraph('Metadatos: ', style='Normal')
    for metadato in exif:
        for c in metadato:
            print(metadato + ': ' + exif[metadato] + '\n')


    return


def inserta_metadata_video(doc, fileName):

    try:
        with exiftool.ExifToolHelper() as et:
            try:
                json_output = et.execute_json('-L', fileName)
            except Exception as e:
                json_output = et.execute('-L', fileName)
                # Eliminar los saltos de linea dobles
                json_output = json_output.replace('\r\n', '\n')
                paragraph = doc.add_paragraph()
                paragraph.style = 'Normal'
                paragraph.line_spacing = WD_LINE_SPACING.SINGLE
                paragraph.space_after = Pt(0)
                paragraph.space_before = Pt(0)
                run = paragraph.add_run(str(json_output))
                run.font.bold = False
                run.font.size = Pt(8)
                return
                print(json_output)

        paragraph = doc.add_paragraph()
        paragraph.style = 'Normal'
        run = paragraph.add_run('Metadatos: ')
        run.font.size = Pt(16)
        run.font.bold = True


        paragraph = doc.add_paragraph()
        paragraph.space_after = Pt(0)
        paragraph.space_before = Pt(0)

        for k,v in json_output[0].items():
            run = paragraph.add_run(str(k))
            run.font.bold = True
            run.font.size = Pt(8)
            run = paragraph.add_run(": " + str(v) + '\n')
            run.font.bold = False
            run.font.size = Pt(8)
            
        return

    except Exception as e:
        print("ERROR metadatos video: ")
        print(e)

        return


# Comprobar si es una imagen por la extensión
def is_image(filename):
    extension = Path(filename).suffix
    if extension.lower() in ['.jpg', '.png', '.jfif', '.exif', '.gif', '.tiff', '.bmp']:
        return True
    return False

# Comprobar si es un video por la extensión
def is_video(filename):
    extension = Path(filename).suffix
    if extension.lower() in ['.mp4', '.avi', '.mov', '.mpg', '.mpeg', '.wmv']:
        return True
    return False

def frames_de_video(filename):
    vidcap = cv2.VideoCapture(filename)
    count = 0
    success = True
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    amount_of_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    imagenes = []

    if fps == 0:
        return imagenes

    while success and count < amount_of_frames:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, count)
        success,image = vidcap.read()
        path = Path(filename)
        fichero_destino = f'{TMP_PATH}{path.stem}_result.jpg'
        fichero_destino = f'{TMP_PATH}{path.stem}_frame'+str(count)+'.jpg'
        cv2.imwrite(fichero_destino, image)
        print('FICHERO_DESTINO: ' + fichero_destino)
        imagenes.append(prepare_image(fichero_destino))
        count+=10*fps
    
    return imagenes






# Creamos el documento
doc = Document()
doc.add_heading('Informe fotografías y videos', 0)

contador = 0
imagenes_total = 0
videos_total = 0

for nombre_directorio, dirs, ficheros in os.walk('./'):
    for fichero in ficheros:
        nombreFichero = nombre_directorio.replace('\\', '/') + "/" + os.path.basename(fichero)
        nombreFicheroOriginal = nombreFichero
        contador += 1
        print('[' + str(contador) + '] '+ nombreFicheroOriginal)
        if contador % 1000 == 0:
            doc.save('demo.docx')
#        if contador > 250:
#            doc.save('demo.docx')
#            sys.exit()


        if filtrar_directorios(nombreFicheroOriginal) == True:
            continue


        if is_image(nombreFichero):

#            continue
            # Comprobamos si hay que convertir la imagen o no
            nombreFichero = prepare_image(nombreFichero)


            paragraph = doc.add_paragraph(nombreFicheroOriginal, style='Heading 2')
            try:
                doc.add_picture(nombreFichero, width=Inches(3.25))
            except Exception as e:
                print(e)
                continue
            try:
                inserta_metadatos(doc, metadatos_imagen(nombreFicheroOriginal))
            except Exception as e:
                print(e)
            imagenes_total += 1

        elif is_video(nombreFichero):
            doc.add_paragraph(nombreFicheroOriginal, style='Heading 2')
            try: 
                frames = frames_de_video(nombreFicheroOriginal)
            except Exception as e:
                print(e)
            paragraph = doc.add_paragraph()
            for frame in frames:
                run = paragraph.add_run()
                run.add_picture(frame, width=Inches(1.75))

            inserta_metadata_video(doc, nombreFicheroOriginal)
            videos_total += 1

        paragraph = doc.add_paragraph()
        insertHR(paragraph)
        paragraph = doc.add_paragraph()
        paragraph.add_run('Imágenes totales: ').font.bold = True
        paragraph.add_run(str(imagenes_total) + '\n').font.bold = False
        paragraph.add_run('Vídeos totales: ').font.bold = True
        paragraph.add_run(str(videos_total) + '\n').font.bold = False


doc.save('demo.docx')