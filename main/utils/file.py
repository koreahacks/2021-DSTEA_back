import os
import subprocess
from pdf2image import convert_from_path
from main.utils.common import Message, Status

FILE_NAME = 'original'
DIR_UPLOAD = 'main/static/upload'
EXT_PPT = ["ppt", "pptx", "pps"]
EXT_PDF = ["pdf"]
TIMEOUT = 20

def pdf2jpgs(pdf_file, board_url):
    images = convert_from_path(pdf_file)
    num_images = len(images)

    for i in range(num_images):
        filename = f'{DIR_UPLOAD}/{board_url}/{str(i)}.jpg'
        images[i].save(filename)

    os.unlink(pdf_file)

    return num_images

def ppt2pdf(ppt_file):
    p = subprocess.Popen(
        ['unoconv', '-f', 'pdf', ppt_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        outs, errs = p.communicate(timeout=TIMEOUT)
    except TimeoutError:
        p.kill()
        outs, errs = p.communicate()
        return Message(Status.INTERNAL_ERROR, "Takes too long.")

    if len(errs) != 0:
        return Message(Status.INTERNAL_ERROR, f"Convert Error: {errs.decode()}")

    for ext in EXT_PPT:
        filename = ppt_file.replace(ext, '.pdf')
    
    os.unlink(ppt_file)
    
    return filename

def save_file(file, board_url):
    directory = f'{DIR_UPLOAD}/{str(board_url)}'
    
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

    with open(f'{directory}/{FILE_NAME}', 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    return f'{directory}/{FILE_NAME}'

def get_images(board_url):
    directory = f'{DIR_UPLOAD}/{str(board_url)}'
    try:
        os.listdir(directory)
    except FileNotFoundError:
        return None