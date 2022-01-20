import requests
import re
import bs4
from fake_useragent import UserAgent 
from pathlib import Path

class handle_download_youtube_video_y2mate:
    '''
    Lớp cho phép lấy link direct video từ trang y2mate và tải về,
    có thể dùng riêng các hàm trong lớp
    input: limit quantity mặc định: '720p', youtube Url, file name, folder path, direct link (nếu chỉ cần sử dụng function download)
    '''
    def __init__(self, youtubeUrl = '', file_name = '', folder_path = '', limitQuantity = '720p', direct_link = ''):
        self.__youtubeUrl = youtubeUrl
        self.__limitQuantity = limitQuantity
        self.__file_name = file_name
        self.__folder_path = folder_path
        self.__direct_link = direct_link
        self.__error = ''
        self.__ua = UserAgent()

    '''
    getter
    '''
    def get_youtubeUrl(self):
        return self.__youtubeUrl
    
    def get_limitQuantity(self):
        return self.__limitQuantity

    def get_file_name(self):
        return self.__file_name
    
    def get_folder_path(self):
        return self.__folder_path
    
    def get_direct_link(self):
        return self.__direct_link
    
    def get_error(self):
        return self.__error

    '''
    setter
    '''
    def set_youtubeUrl(self, youtubeUrl):
        self.__youtubeUrl = youtubeUrl
    
    def set_limitQuantity(self, limitQuantity):
        self.__limitQuantity = limitQuantity

    def set_file_name(self, file_name):
        self.__file_name = file_name
    
    def set_folder_path(self, folder_path):
        self.__folder_path = folder_path
    
    def set_direct_link(self, direct_link):
        self.__direct_link = direct_link
    
    '''
    function
    '''

    def y2mateCrawlLink(self):
        '''
        Gửi yêu cầu lấy link lên server
        input: link youtube, limit quantity (default = '720p')
        output: error
        '''

        headers = {
                'accept-language':'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'user-agent': self.__ua.random,
                'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with':'XMLHttpRequest',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }

        try:
            requestUrlStep1 = 'https://www.y2mate.com/mates/en163/analyze/ajax'

            formDataStep1 = {
                'url': self.__youtubeUrl,
                'q_auto': '0',
                'ajax': '1'
            }

            dataStep1 = requests.post(requestUrlStep1, headers = headers, data = formDataStep1)
            htmlResultStep1 = dataStep1.json()['result'].replace('\\', '')

            soup = bs4.BeautifulSoup(htmlResultStep1, 'html.parser')
            regex_quantity = re.compile('([0-9]{3,4})p')
            list_a_tag_quantity = soup.findAll('a', {'rel': 'nofollow', 'href': '#'})
            list_quantity = [a.text.split(' ')[1] for a in list_a_tag_quantity]
            list_quantity_new = [q for q in list_quantity if regex_quantity.match(q)]

        except Exception as e:
            return '%s'%e

        regex_id = 'k__id = "(.*?)"'
        regex_v_id = 'k_data_vid = "(.*?)"'
        _id = re.search(regex_id, htmlResultStep1).group(1)
        v_id = re.search(regex_v_id, htmlResultStep1).group(1)

        quantity = ''
        if (self.__limitQuantity in list_quantity_new) == False:
            list_temp = [i for i in list_quantity_new if int(i[:-1]) < int(self.__limitQuantity[:-1])]
            quantity = list_temp[0]
        else:
            quantity = self.__limitQuantity

        '''
        Lấy link điều hướng
        '''
        try:
            requestUrlStep2 = 'https://www.y2mate.com/mates/convert'

            formDataStep2 = {
                'type': 'youtube',
                '_id': _id,
                'v_id': v_id,
                'ajax': '1',
                'ftype': 'mp4',
                'fquality': quantity[:-1]
            }

            dataStep2 = requests.post(requestUrlStep2, headers=headers, data=formDataStep2)
            htmlResultStep2 = dataStep2.json()['result']

            regex_link = '<a href="(.*?)"'
            link = re.search(regex_link, htmlResultStep2).group(1)

            del dataStep1, dataStep2
            self.__direct_link = link
            return ''
        
        except Exception as e:
            return '%s'%e
        
    def downloadVideo(self):
        '''
        Tải video khi biết direct link, folder_path, fileName
        input: direct link, file name, contain folder path
        output: error
        attetion: Các link direct có giới hạn phiên làm việc
        '''

        headers = {
            'user-agent': self.__ua.random
        }

        if self.__folder_path == '':
            self.__folder_path = str(Path().resolve())
            self.__folder_path = self.__folder_path.replace('\\', '/')

            chk = self.__folder_path + '/Video download/'

            if Path(chk).exists() == False:
                p = Path('Video download')
                p.mkdir(parents=True, exist_ok=True)

            self.__folder_path = chk

        else:
            self.__folder_path = self.__folder_path.replace('\\', '/')
            if self.__folder_path[-1] != '/':
                self.__folder_path = self.__folder_path + '/'

        file_tails = 'MP4|AVI|MOV|FLV|WMV|mp4|avi|mov|flv|wmv'

        regex = re.compile(f'.*({file_tails})')
        if not regex.match(self.__file_name):
            return 'unknow format file'

        try:
            res = requests.get(self.__direct_link, headers=headers, stream=True, timeout = 10, verify=False)
        except Exception as e:
            return '%s'%e

        try:
            with open(self.__folder_path + self.__file_name, 'wb') as out_file:
                for chunk in res.iter_content(chunk_size = 1024*1024): 
                    if chunk: 
                        out_file.write(chunk)
        except Exception as e:
            return '%s'%e

        del res
        return ''
    
    def handle(self):
        '''
        Lấy direct link và tải xuống
        '''
        err1 = self.y2mateCrawlLink()
        if err1 != '':
            self.__error = err1 + ' funtion 1'
            return
        
        err2 = self.downloadVideo()
        if err2 != '':
            self.__error = err2 + ' funtion 2'
            return

    def reset(self, folder_path = '', limitQuantity = ''):
        '''
        Reset các value trong class trừ folder path và limitQuantity, nếu muốn thay đổi thì truyền path khác vào hàm
        '''
        self.__youtubeUrl = ''
        self.__file_name = ''
        if folder_path != '':
            self.__folder_path = folder_path
        if limitQuantity != '':
            self.__limitQuantity = limitQuantity
        self.__direct_link = ''
        self.__error = ''
        

if __name__ == '__main__':
    youtubeLink = 'https://www.youtube.com/watch?v=psZ1g9fMfeo'
    name = 'vid1.mp4'
    class1 = handle_download_youtube_video_y2mate(youtubeUrl = youtubeLink, file_name = name)
    class1.handle()
    print(f'Lỗi: {class1.get_error()}')
    class1.reset()


        
