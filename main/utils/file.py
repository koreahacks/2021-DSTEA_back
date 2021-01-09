from pdf2image import convert_from_path

DIR_UPLOAD = 'main/static/upload'

def pdf2jpgs(pdf_file, board_url):
    """
    pdf파일을 페이지별로 나누어 jpg파일로 저장합니다.
    jpg파일 위치는 main/static/upload/<board_url>/<index>.jpg 입니다.
    페이지가 3개일 경우 0.jpg, 1.jpg, 2.jpg와 같이 저장됩니다.

    for i in range(0, <return value>):
        r.append(f'main/static/upload/{board_url}/{i}.jpg')
    
    와 같은 방법으로 저장된 jpg파일을 참조할 수 있습니다.

    :param pdf_file: pdf파일 경로
    :param board_url: board_url
    :returns: jpg파일 개수
    """
    images = convert_from_path(pdf_file)
    num_images = len(images)

    for i in range(num_images):
        filename = f'{DIR_UPLOAD}/{board_url}/{str(i)}.jpg'
        images[i].save(filename)

    return num_images