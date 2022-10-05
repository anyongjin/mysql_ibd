[for chinese](readme.cn.md)

# Introduction
This is a script for importing database tables from mysql's ibd file, targeting the innodb storage engine.  
If your data table is using the MyISAM engine, please go to the [mysql documentation](https://dev.mysql.com/doc/refman/8.0/en/import-table.html) and use `import table from` to restore table data from frm and MYD files.  
For the innodb engine, in versions earlier than mysql8, each table has a frm file and an ibd file in the data directory. The former is the table structure and the latter is the table data. 
Starting from mysql8, metadata such as table structure information is saved through sdi, and sdi is embedded in the ibd file. So a table corresponds to only one data file.  

For the case where there are frm files in versions before mysql8, mysql provides the `mysqlfrm` tool to generate table building statements from frm. 
However, for versions after mysql8, only the `ibd2sdi` tool is provided to generate sdi files (table structures in JSON form) from ibd files, and sql statements cannot be generated directly.  

This project supports the following two functions:
* For versions after mysql8, support for generating table statements from ibd
* For any version of mysql, after the table structure is restored, the ibd file can be imported into table data in batches

# how to use
## There are frm and ibd files
Please refer to this article or this answer to generate the create table statement from the frm file and execute the create table structure.   
If there are few tables, you can manually import table data from ibd directly according to the method in the above article.   
If there are many tables, you can use this script to modify the config.yml configuration file, update the directory and database information, and use the command python main.py load_data to import data into the database.

## only ibd files
Try to keep the new database version consistent with the original database version, otherwise errors may occur when importing data.

1. Modify the `input_ibds` and `output` items in `config.yml` and set them to the ibd file directory
2. Execute `python main.py tosql` to generate sdi and sql files from ibd files
3. Check sql file and execute, create empty table
4. Modify the `mysql_db_dir` and `db_info` items in `config.yml` and set them to the data directory of the new database
5. Execute `python main.py load_data` to batch import data from the ibd file to the database(Please run on the database server)

# related question
**Schema mismatch (Clustered index validation failed. Because the .cfg file is missing, table definition of the IBD file could be different. Or the data file itself is already corrupted.)**  
Occasionally this error occurs when importing ibd after mysql8. Use the ibd2sdi tool to generate sdi from the new table, and compare the old and new sdi files, which are basically the same, and the reason is temporarily uncertain. Encountering this error temporarily can only use other means to restore the table data. If any friend has solved this problem, please open an issue and let me know~
