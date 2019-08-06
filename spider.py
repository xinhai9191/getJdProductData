# coding:utf-8
import requests
from bs4 import BeautifulSoup
import threading
from SQL import save_mysql  #导入sql存储数据
import json
import queue

class Mythread(threading.Thread):
    def __init__(self,fun):
        threading.Thread.__init__(self)
        self.fun = fun
    def run(self):
        self.fun()

class spiders:
    def setPage(self, page):
        self.url = 'https://search.jd.com/Search?keyword=%E9%A3%9F%E5%93%81&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=5&wq=%E9%A3%9F%E5%93%81&page=' + str(
            page)
        self.headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        self.search_urls = 'https://search.jd.com/s_new.php?keyword=%E9%A3%9F%E5%93%81&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&offset=3&wq=%E9%A3%9F%E5%93%81&page={0}&s=26&scrolling=y&pos=30&show_items={1}'
        self.pids = set()  # 页面中所有的id,用来拼接剩下的30张图片的url,使用集合可以有效的去重
        self.img_urls = set()  # 得到的所有图片的url
        self.search_page = page + 1  # 翻页的作用
        self.sql = save_mysql()  # 数据库保存

    # 得到每一页的网页源码
    def get_html(self):
        res = requests.get(self.url, headers=self.headers)
        html = res.text
        return html

    # 得到每一个页面的id
    def get_pids(self):
        html = self.get_html()
        soup = BeautifulSoup(html, 'lxml')
        lis = soup.find_all("li", class_='gl-item')
        for li in lis:
            data_pid = li.get("data-pid")
            if (data_pid):
                self.pids.add(data_pid)
    # 得到每一个页面的图片和一些数据，由于这是aiax加载的，因此前面一段的img属性是src，后面的属性是data-lazy-img
    def get_data(self):
        html = self.get_html()
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find_all("div", class_='p-img')  # 图片
        for div in divs:
            aurl = div.find("a").get('href')
            if (aurl.find('https:') < 0):
                aurl = "https:" + aurl

            try:
                inter = requests.get(aurl, headers=self.headers).text
            except:
                continue
            sInter = BeautifulSoup(inter, 'lxml')
            sku_name = sInter.find("div", class_='sku-name').text.strip()
            li = sInter.find("ul", class_='parameter2').findAll('li')
            prodCode = li[1].text.replace("商品编号：", "")
            prourl = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" +prodCode
            wbdata = requests.get(prourl, headers=self.headers).text
            data = json.loads(wbdata)
            data = data['CommentsCount']
            evaluate = data[0]['DefaultGoodCount']
            prourl = "https://c0.3.cn/stock?skuId=" + prodCode + "&area=2_2823_51974_0&cat=1320,1583,1590"
            wbdata = requests.get(prourl, headers=self.headers).text
            data = json.loads(wbdata)
            data = data['stock']
            price = data['jdPrice']['p']
            prourl = "https://cd.jd.com/promotion/v2?skuId=" + prodCode + "&area=2_2823_51974_0&cat=1320,1583,1590"
            wbdata = requests.get(prourl, headers=self.headers).text
            data = json.loads(wbdata)
            content = ""
            for promote in data['prom']['pickOneTag']:
                content = content + promote['name']

            image = sInter.find("img", id='spec-img').get('data-lazy-img')
            img = sInter.find("img", id='spec-img').get('src')
            if img:
                image = img
            norm = sInter.find("div", id='summary-weight').find('div', class_='dd').text

            self.sql.save_data(sku_name, price, evaluate, image, prodCode, content, norm)
            commentUrl = "https://sclub.jd.com/comment/productPageComments.action?productId=" +prodCode+"&score=0&sortType=5&page=0&pageSize=1000"
            jdHeaders = {
                'Connection': 'Keep-Alive',
                'Accept': 'text/html, application/xhtml+xml, */*',            
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
                'Referer':'https://item.jd.com/%d.html'%(int(prodCode)),
                'Host':'sclub.jd.com'
            }
            wbdata = requests.get(commentUrl, headers=jdHeaders).text
            print(wbdata)
            data = json.loads(wbdata)
            

    def main(self):
        while not q.empty():
            self.setPage(q.get())
            self.get_data()

if __name__ == '__main__':
    threads = []
    q = queue.Queue()
    for task in range(100):
        q.put(task)
    for i in range(3):
        thread = Mythread(spiders().main)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
