import requests
from fake_useragent import UserAgent
import shutil
import re
from pathlib import Path

def downloadImage(image_url, folder_path = ''):
    '''
    Tải file ảnh khi biết link và đường dẫn lưu file, nếu không có đường dẫn lưu file thì sẽ mặc đinh tạo tự động
    input: image url, contain folder path
    output: error, contain folder path
    '''
    if folder_path == '':
        folder_path = str(Path().resolve())
        folder_path = folder_path.replace('\\', '/')

        chk = folder_path + '/Image download/'
        if Path(chk).exists() == False:
            p = Path('Image download')
            p.mkdir(parents=True, exist_ok=True)

        folder_path = chk
    else:
        folder_path = folder_path.replace('\\', '/')
        if folder_path[-1] != '/':
            folder_path = folder_path + '/'

    file_tails = 'jpg|jpeg|png|gif|tiff|psd|pdf|eps|ai|indd|raw|JPG|JPEG|PNG|GIF|TIFF|PSD|PDF|EPS|AI|INDD|RAW'

    regex = re.compile(f'.*({file_tails})')
    if not regex.match(image_url):
        return 'unknow format file', ''

    ua = UserAgent(fallback=image_url)

    headers = {
        'user-agent': ua.random
    }

    try:
        res = requests.get(image_url, stream = True, headers = headers, timeout = 10, verify = False)
    except Exception as e:
        return '%s'%e, ''

    try:
        file_name = image_url.split('/')[-1]
        with open(folder_path + file_name, 'wb+') as out_file:
            shutil.copyfileobj(res.raw, out_file)
    except Exception as e:
        return f'{e}', ''

    del res
    return '', folder_path

if __name__ == '__main__':
    image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/220px-Image_created_with_a_mobile_phone.png'
    err, file_path = downloadImage(image_url)

