#coding:utf-8
import MySQLdb as db

#将得到的数据存入数据库中mysql
class save_mysql:
    def __init__(self):
        self.user='root'
        self.password=''
        self.host='localhost'
        self.database='product'
    def get_connection(self):
        return db.connect(user="root",passwd="",host="localhost",db="product",charset="utf8")

    def save_data(self, sku_name, price, evaluate, image, prodCode, content, norm):
        conn = self.get_connection()
        cursor = conn.cursor()
        is_promote = 0
        if len(content.strip()) > 0:
            is_promote = 1
        cursor.execute("insert into product(prod_code,prod_name,image,norm,price,promote_content,sale_num,evaluate,is_promote) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (prodCode, sku_name, image, norm, price, content, evaluate, evaluate, is_promote))   #将img_url插入到数据库中
        conn.commit()
