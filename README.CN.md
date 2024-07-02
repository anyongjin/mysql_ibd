# ˵��

����һ�����ڴ�mysql��ibd�ļ��������ݿ���Ľű������innodb�洢���档
����������ݱ�ʹ�õ���MyISAM���棬���Ʋ�[mysql�ĵ�](https://dev.mysql.com/doc/refman/8.0/en/import-table.html)��ʹ��`import table from`��frm��MYD�ļ��ָ������ݡ�
����innodb���棬��mysql8��ǰ�İ汾�£�ÿ����������Ŀ¼����frm�ļ���ibd�ļ���ǰ���Ǳ��ṹ�������Ǳ����ݡ�
��mysql8��ʼ�����Ľṹ��Ϣ��Ԫ����ͨ��sdi���棬sdiǶ�뵽ibd�ļ����档����һ����ֻ��Ӧһ�������ļ���

����mysql8֮ǰ�汾��frm�ļ��������mysql�ṩ��`mysqlfrm`���߿��Դ�frm���ɽ�����䡣
������mysql8֮��汾��ֻ�ṩ��`ibd2sdi`���ߴ�ibd�ļ�����sdi�ļ���JSON��ʽ�ı��ṹ��������ֱ������sql��䡣

�����Ŀ֧���������������ܣ�

* ����mysql8֮��汾��֧�ִ�ibd���ɽ������
* ������汾mysql��֧�ֱ��ṹ�ָ���**ibd�ļ��������������**

# ���ʹ��

## ��frm��ibd�ļ�

��ο�[��ƪ����](https://jamesingold.com/restoring-mysql-database-frm-ibd)��[����ش�](https://dba.stackexchange.com/a/71785)����frm�ļ����ɽ�����䣬ִ�д������ṹ��
������Ƚ��٣�����ֱ�Ӱ�����������еķ������ֶ���ibd��������ݡ�
������Ƚ϶࣬����ʹ�ñ��ű����޸�`config.yml`�����ļ�������Ŀ¼�����ݿ���Ϣ��ʹ������`python main.py load_data`�������ݵ����ݿ⼴�ɡ�

## ֻ��ibd�ļ�
>
> �������������ݿ��ԭ���ݿ�汾һ�£���������ڵ�������ʱ���ִ���
> ������ҵ�ԭʼ����sql�Ļ�������ִ�е�2����ֱ��ʹ��ԭʼsql�����ձ����ɱ��ⲻ��Ҫ�ı�����

0. ȷ��mysql 8�Ѱ�װ�Һ�ibd�ļ���Ӧ�����ݿ�汾һ�£�����mysql��binĿ¼��ϵͳ��������������where�������ibd2sdi��ʧ�ܣ�
1. �޸�`config.yml`�е�`input_ibds`��`output`�����Ϊibd�ļ�Ŀ¼
2. ִ��`python main.py tosql`����ibd�ļ�����sdi��sql�ļ����������ȱ�ٰ�������ʹ��`pip install xxx`��װȱ�ٵİ���
3. ���sql�ļ���ִ�У������ձ�
4. �޸�`config.yml`��`mysql_dbconnection_info`db_info`�����Ϊ�����ݿ������Ŀ¼
5. ִ��`python main.py load_data`��ibd�ļ������������ݵ����ݿ⣨�������ݿ�����������У�

# �������

**Schema mismatch (Clustered index validation failed. Because the .cfg file is missing, table definition of the IBD file could be different. Or the data file itself is already corrupted.)**
��mysql8֮���ibd����ʱ��ż��������������ʹ��`ibd2sdi`���ߴ��±�����sdi���Ա��¾ɵ�sdi�ļ�����������һ���ġ�issues���������ᵽ���������ɵ�sql��ԭʼsql�в��쵼�±��ṹ��Ϣ����ȫƥ�䣬��ͨ������������������������`INDEX`��Ϊ`KEY`����ˣ�����Ҳ�������������������Ϊһ������[#14](/../../issues/14)

**������ʼֵ����**
��ibd�ļ��������ݺ󣬱��������е���ʼֵ��Ȼ��0���ڲ��������ݵ�ʱ��ᱨ������ʹ�����������ֶ���ѯ�ָ���

```sql
select max(id) from `mytable`;
ALTER TABLE `mytable` AUTO_INCREMENT=val+1
```
