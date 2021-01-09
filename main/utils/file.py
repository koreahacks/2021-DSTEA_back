import subprocess
from pdf2image import convert_from_path

DIR_UPLOAD = 'main/static/upload'
EXT_PPT = ["ppt", "pptx", "pps"]
TIMEOUT = 20

def pdf2jpgs(pdf_file, board_url):
    images = convert_from_path(pdf_file)
    num_images = len(images)

    for i in range(num_images):
        filename = f'{DIR_UPLOAD}/{board_url}/{str(i)}.jpg'
        images[i].save(filename)

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
        return None

    if len(errs) != 0:
        return None

    for ext in EXT_PPT:
        filename = ppt_file.replace(ext, '.pdf')
    
    return filename