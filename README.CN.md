# 说明
这是一个用于从mysql的ibd文件导入数据库表的脚本，针对innodb存储引擎。
如果您的数据表使用的是MyISAM引擎，请移步[mysql文档](https://dev.mysql.com/doc/refman/8.0/en/import-table.html)，使用`import table from`从frm和MYD文件恢复表数据。
对于innodb引擎，在mysql8以前的版本下，每个表在数据目录下有frm文件和ibd文件，前者是表结构，后者是表数据。
从mysql8开始，表的结构信息等元数据通过sdi保存，sdi嵌入到ibd文件里面。所以一个表只对应一个数据文件。

对于mysql8之前版本有frm文件的情况，mysql提供了`mysqlfrm`工具可以从frm生成建表语句。
但对于mysql8之后版本，只提供了`ibd2sdi`工具从ibd文件生成sdi文件（JSON形式的表结构），不能直接生成sql语句。

这个项目支持了下面两个功能：
* 对于mysql8之后版本，支持从ibd生成建表语句
* 对任意版本mysql，支持表结构恢复后，**ibd文件批量导入表数据**

# 如何安装

## 前置条件
1. 确保mysql 8已安装且和ibd文件对应的数据库版本一致；
2. 添加mysql的bin目录到系统环境变量`Path`中，以确保`ibd2sdi`可直接使用

## 本地安装
1. 下载项目源码: `git clone ...`
2. 准备python3环境，并确保pip可用
3. 安装依赖：`pip install requirements.txt`

## docker安装
使用镜像：`ghcr.io/anyongjin/mysql_idb:mysql-8.4`（可根据需要更改mysql版本）
也可从`Dockerfile`构建镜像并使用

## k8s中使用
复制`k8s-sample.yaml`文件，并根据需要更改值（您还需要一个新数据库+Datadir访问的活动实例），并将其应用于集群中，然后执行到新创建的pod中

# 如何使用
## 有frm和ibd文件
请参考[这篇文章](https://jamesingold.com/restoring-mysql-database-frm-ibd)或[这个回答](https://dba.stackexchange.com/a/71785)，从frm文件生成建表语句，执行创建表结构。
如果表比较少，可以直接按上面的文章中的方法，手动从ibd导入表数据。
如果表比较多，可以使用本脚本，修改`config.yml`配置文件，更新目录和数据库信息，使用命令`python main.py load_data`导入数据到数据库即可。

## 只有ibd文件
> 尽量保持新数据库和原数据库版本一致，否则可能在导入数据时出现错误。
> 如果能找到原始建表sql的话，无需执行第2步，直接使用原始sql创建空表，可避免不必要的报错。

1. 修改`config.yml`中的`input_ibds`和`output`项，设置为ibd文件目录
2. 执行`python main.py tosql`，从ibd文件生成sdi和sql文件
3. 检查sql文件并执行，创建空表
4. 修改`config.yml`中`mysql_db_dir`和`db_info`项，设置为新数据库的数据目录
5. 执行`python main.py load_data`从ibd文件批量导入数据到数据库（请在数据库服务器上运行）

# 相关问题
**Schema mismatch (Clustered index validation failed. Because the .cfg file is missing, table definition of the IBD file could be different. Or the data file itself is already corrupted.)**
在mysql8之后的ibd导入时，偶尔会出现这个错误。使用`ibd2sdi`工具从新表生成sdi，对比新旧的sdi文件，基本都是一样的。issues中有朋友提到可能是生成的sql和原始sql有差异导致表结构信息不完全匹配，他通过将定义主键和索引的语句从`INDEX`改为`KEY`解决了，可能也有其他错误情况，可作为一个方向：[#14](/../../issues/14)

**自增起始值问题**
从ibd文件导入数据后，表的自增列的起始值依然是0，在插入新数据的时候会报错，可使用下面命令手动查询恢复：
```sql
select max(id) from `mytable`;
ALTER TABLE `mytable` AUTO_INCREMENT=val+1
```
