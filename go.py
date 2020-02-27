import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import time


URL='http://h5.eqxiu.com/s/Cpmop6jW'
USERAGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1'

SESSION=requests.Session()
SESSION.headers={'User-Agent':USERAGENT}

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", USERAGENT)
DRIVER = webdriver.Firefox(firefox_profile=profile,executable_path='./geckodriver')
DRIVER.set_window_size(480, 800)



paths=URL.split('/')

for path in paths:
    if path !='':

        BASEPATH=path+'/'

def mk_dir(dir=''):
    try:
        os.mkdir(BASEPATH+dir)
    except Exception as e:
        # print(e)
        # print(str(e))
        pass



class Static:
    def __init__(self,tag):
        self.tag=tag
        self.old_tag_str=str(tag)
        self.new_tag_str=''
        self.url=''
        self.filetype=''
        self.type=''
        self.filename=''
    
    def save(self,name):
        print('-----------------SAVING-----------------')
        
        tag=self.tag
        try:
            self.url=tag['href']
        except KeyError:
            self.url=tag['src']
        except Exception as e:
            print(str(e))
            raise

        if self.url[:4] != 'http':
            self.url=URL + self.url

   
        try:
            r=SESSION.get(self.url)
            self.type=r.headers['Content-Type'].split('/')[0]
            if self.type == 'application':
                self.type= 'js'
                self.filetype='js'
            elif self.type == 'image':
                self.type= 'img'
                self.filetype=r.headers['Content-Type'].split('/')[1]
            elif self.type == 'text':
                self.filetype=r.headers['Content-Type'].split('/')[1]
            else:
                print(self.type)
                raise
            
            self.filename=name+'.'+self.filetype
            
            print('type:',self.type,'\nfiletype',self.filetype,'\nfilename',self.filename)
            
            mk_dir(self.type)
        
            with open(BASEPATH+self.type+'/'+self.filename,'wb',) as f:
                f.write(r.content)
            self.new_tag_str=self.old_tag_str.replace(self.url,self.type+'/'+self.filename)
            return True

        except Exception as e:
            print('ERROR IN FILE SAVEING')
            print(str(e))
            return False


class LocalStatic:
    def __init__(self,tag):
        self.tag=tag
        self.old_tag_str=str(tag)
        self.new_tag_str=''
        self.code=''
        self.type=''
        self.filename=''
    
    def fix(self,filename):
        tag=self.tag
        self.code=tag.text
        if tag.name=='script':
            self.type='js'
        elif tag.name=='style':
            self.type='css'
        else :
            print('UNKNOW INSTATIC TYPE')
        
        self.filename=filename+'.'+self.type

        # 创建类型路径
        mk_dir(self.type)
        

    def save(self):
        print('-----------------SAVING-----------------')
        try:
            print('type:',self.type,'\nfilename',self.filename)
            # 保存文件
            with open(BASEPATH+self.type+'/'+self.filename,'w',) as f:
                f.write(self.code)
            # 将url指向文件
            if self.type == 'js':
                self.new_tag_str='<script src="js/'+self.filename+'"></script>'
            elif self.type == 'css':
                self.new_tag_str='<link rel="stylesheet" href="css/'+self.filename+'"></script>'
            else:
                print('UNKNOW INSTATIC TYPE')

            return True

        except Exception as e:
            print(str(e))
            return False


if __name__ == '__main__':
    # print(BASEPATH)
    
    mk_dir()

    # r=SESSION.get(URL)
    # encode=r.apparent_encoding
    # # print(r.apparent_encoding)
    # r.encoding=encode
    # html=r.text

    DRIVER.get(URL)
    
    time.sleep(30)
    html=DRIVER.page_source
    DRIVER.quit()

    soup=BeautifulSoup(html,'html.parser')

    with open(BASEPATH + 'page_source_old.html','w',encoding='utf8') as f:
        f.write(str(soup))

    new_page_source=str(soup)

    # 获取文件标签
    tele_tags=[]
    local_tages=[]
    local_tages.extend( soup.find_all('style'))
    tele_tags.extend( soup.find_all('link'))
    tele_tags.extend( soup.find_all('img'))
    
    for tag in soup.find_all('script'):
        try:
            print(tag['src'])
            tele_tags.append(tag)
        except KeyError:
            tag.text
            local_tages.append(tag)
        except Exception as e:
            print('UNKNOW SCRIPT TYPE')
            print(str(e))
            raise
    

    # 操作远程文件
    n=0
    for tag in tele_tags:
        static=Static(tag)
        if static.save(str(n)):
            new_page_source=new_page_source.replace(static.old_tag_str,static.new_tag_str)
            n+=1
    
    # 操作本地文件
    for tag in local_tages:
        local_static=LocalStatic(tag)
        local_static.fix(str(n))
        if local_static.save():
            new_page_source=new_page_source.replace(local_static.old_tag_str,local_static.new_tag_str)
        n+=1

    # 插入控制脚本
    basejs='\n<script type="text/javascript" src="//res.hduofen.cn/js/zaaxstat.js?id=hfUsC7Di"></script>\n'
    new_page_source = new_page_source.replace('</head>',basejs+'</head>')
    addonjs='''
                \n
                <div>
                    <span class="zaax-wxh">默认微信号</span>
                    <span class="zaax-wxname">默认微信号客服名称</span>
                    <span class="zaax-wxsex">默认性别</span>
                    <img class="zaax-qr" src="默认二维码地址"/>
                </div>
                \n
            '''
    new_page_source = new_page_source.replace('</body>',addonjs+'</body>')

    # SAVE
    with open(BASEPATH+ 'page_source_new.html','w',encoding='utf8') as f:
        f.write(new_page_source)