import requests,re,MySQLdb,os
from bs4 import BeautifulSoup
headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47"}    
real_dir = os.getcwd()  #真实绝对路径
wallpaperdic = []   #壁纸种类url列表
wallpapers = {}     #壁纸名和url


class Mysql():  #处理数据库
    def __init__(self) :
        db = MySQLdb.connect("localhost", "root", "20090330huang", "wallpaper", charset='utf8' )     #打开数据库
        self.db = db
    
    #主页解析
    def insert_select(self):
        cursor = self.db.cursor()
        for i in range(len(wallpaperdic)):
            n = i+1
            sql = (f"INSERT INTO walls(id,url) VALUES('{n}','{wallpaperdic[i]}')")
            cursor.execute(sql)
            self.db.commit()
        self.db.close()
    
    #单个壁纸url查询
    def select(self):
        url = []
        cursor = self.db.cursor()
        sql = "SELECT * FROM walls"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            url.append(row[1])
        self.db.close()
        return url

    #上传单个图片url
    def insert_one(self,filename,url):
        cursor = self.db.cursor()
        sql = (f"INSERT INTO wallpapers(name,url) VALUES('{filename}','{url}')")
        cursor.execute(sql)
        self.db.commit()
        self.db.close()
        
def main(real_dir):
    #主页访问
    url = "https://wall.alphacoders.com/finding_wallpapers.php?lang=Chinese"
    main = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(main.text,'lxml')

    #解析壁纸种类url
    rule1 = re.compile(r'<a class="list-group-item" href="https://(wall.alphacoders.com/.*?)" .*?>')
    for i in soup.find_all('a', class_='list-group-item'):
        if(len(re.findall(rule1,str(i)))):
            wallpaperdic.append(re.findall(rule1,str(i))[0])
        Mysql().insert_select()

    #单个分类访问
    paper = []
    papername = []
    urls = Mysql().select()
    for i in urls:
        for j in range(500):
            n = j + 1
            #获取壁纸分类
            url = (f"https://{i}&page={n}")
            html = requests.get(url=url,headers=headers)

            #解析壁纸
            soup = BeautifulSoup(html.text,'lxml')
            rule1 = re.compile('<img .*? src="(.*?)".*?>')
            for link in soup.find_all('img',class_='img-responsive'):
                if(len(re.findall(rule1,str(link)))):
                    paper.append(re.findall(rule1,str(link))[0])
            rule2 = re.compile('<img alt="(.*?)" .*?/>')
            for link in soup.find_all('img',class_='img-responsive'):
                if(len(re.findall(rule2,str(link)))):
                    papername.append(re.findall(rule2,str(link))[0])
            
            #将壁纸添加到字典
            n = len(papername)
            for link in range(n):
                wallpapers[str(papername[link])] = str(paper[link])
            

            #下载图片到本地
            illegal = ['|',' ','\\']
            for link in list(wallpapers.keys()):    #link是文件名，filename是文件相对路径
                url = wallpapers[link]
                data = requests.get(url=url,headers=headers).content
                filename = (f"{real_dir}/static/wallpapers/{link}.jpg")
                #去除非法字符
                for illega in illegal:
                    if illega in filename:
                        filename = filename.replace(illega,'_')
                with open(filename,'wb') as f:
                    f.write(data)
                #print(f"{filename}下载完成！！！")

                #将下载下来的图片的相对路径存储到mysql数据库
                Mysql().insert_one(filename=link,url=filename)  #link是文件名，filename是文件相对路径


if __name__ == "__main__":
    #print(real_dir)
    try:
        main(real_dir=real_dir)
    except:
        pass