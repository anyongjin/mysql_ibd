[For Chinese 中文](readme.cn.md)

# Introduction

This is a script for importing database tables from mysql's ibd file, targeting the innodb storage engine.

If your table is using the MyISAM engine, please go to the [mysql documentation](https://dev.mysql.com/doc/refman/8.0/en/import-table.html) and use `import table from` to restore table data from frm and MYD files.

For the innodb engine, in versions earlier than mysql 8, each table has a `frm` file and an `ibd` file in the data directory. The `frm` file is used to save table structure.

Start from mysql 8, the table structure is saved with sdi, which is embedded in the `ibd` file. So there is only one `{table}.ibd` file for each table.

Mysql provides the `mysqlfrm` tool to generate table building statements from `frm` for versions earlier than mysql 8,
However, for versions after mysql 8, only the `ibd2sdi` tool is provided to generate sdi files (table structures in JSON format) from ibd files, and sql statements cannot be generated directly.

This project supports the following two functions:

* For versions after mysql 8, support for generating table statements from ibd
* For any version of mysql, after the table structure is restored, the ibd file can be imported into table data in batches

# How to use

## Both frm and ibd files exists (versions earlier than mysql 8)

Please refer to [this article](https://jamesingold.com/restoring-mysql-database-frm-ibd) or [this answer](https://dba.stackexchange.com/a/71785) to generate the create table statement from the frm file and execute the create table structure.

If there are few tables, you can manually import table data from ibd directly according to the method in the above article.

If there are many tables, you can use this script to modify the `config.yml` configuration file, update the directory and database information, and use the command `python main.py load_data` to import data into the database.

## only ibd files (versions after mysql 8)
>
> Try to keep the new database version consistent with the original database version, otherwise errors may occur when importing data.
> If the original table creation SQL can be found, there's no need to proceed with step 2; instead, use the original SQL to create an empty table, which can avoid unnecessary errors.

0. Make sure that mysql 8 is installed and the database version corresponding to the ibd file is consistent, and add the `bin` directory of mysql to the system environment variable (otherwise the `where ibd2sdi` command will fail)
1. Modify the `input_ibds` and `output` items in `config.yml` and set them to the ibd file directory
2. Execute `python main.py tosql` to generate sdi and sql files from ibd files (If you encounter a missing package error, please use pip install xxx to install the missing package.)
3. Check sql file and execute, create empty table
4. Modify the `mysql_db_dir` and `connection_info` items in `config.yml` and set them to the data directory of the new database
5. Execute `python main.py load_data` to batch import data from the ibd file to the database(Please run on the database server)

# related question

**Schema mismatch (Clustered index validation failed. Because the .cfg file is missing, table definition of the IBD file could be different. Or the data file itself is already corrupted.)**

Occasionally this error occurs when importing ibd after mysql8. Use the ibd2sdi tool to generate sdi from the new table, and compare the old and new sdi files, which are basically the same. In the issues, a friend mentioned that the difference between the generated SQL and the original SQL might cause the table structure information to not match completely. He solved it by changing the statements that define primary keys and indexes from INDEX to KEY. There might also be other error situations, which could be considered as a direction: [#14](/../../issues/14).

**Bad start value for auto-increment column**

After importing data from the ibd file, the starting value of the auto-increment table is still 0, and an error would occur while inserting new data. You can use the following command to manually query and fix it:

```sql
select max(id) from `mytable`;
ALTER TABLE `mytable` AUTO_INCREMENT=val+1
```
