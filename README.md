[For Chinese 中文](README.CN.md)

[![Docker Tags](https://ghcr-badge.egpl.dev/anyongjin/mysql_ibd/tags?trim=major&color=green_2&label=Docker%20Tags&ignore=*.sig)](https://ghcr.io/anyongjin/mysql_ibd/)
![GitHub branch check runs](https://img.shields.io/github/check-runs/anyongjin/mysql_ibd/master)
![Python Version](https://img.shields.io/badge/python-3.12-green)

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

# How to install

In Docker or K8s no steps required just use pre built image or build one from Dockerfile in project

If you are not using Docker or K8s

0. Ensure Python3.12 or newer is install & Clone Project
1. Make sure that `ibd2sdi` command is available (install mysql server package).
2. Install Python3 and ensure Pip is installed
3. Run `pip install -r requirements.txt`

> you are ready to go... refer to How to use section to continue

# How to use

## Both frm and ibd files exists (versions earlier than mysql 8)

Please refer to [this article](https://jamesingold.com/restoring-mysql-database-frm-ibd) or [this answer](https://dba.stackexchange.com/a/71785) to generate the create table statement from the frm file and execute the create table structure.

If there are few tables, you can manually import table data from ibd directly according to the method in the above article.

If there are many tables, you can use this script to modify the `config.yml` configuration file, update the directory and database information, and use the command `python main.py load_data` to import data into the database.

## only ibd files (versions after mysql 8)
>
> Try to keep the new database version consistent with the original database version, otherwise errors may occur when importing data.
> If the original table creation SQL can be found, there's no need to proceed with step 2; instead, use the original SQL to create an empty table, which can avoid unnecessary errors.

1. Modify config.yml file according to it's comments (use `-c` or `--config` in your commands if you want to have config in another location)
2. Execute `python main.py tosql` to generate sdi and sql files from ibd files (set `apply_sql` to `true` in config to run them on provided connection, but it's better to check/review output then run that manually)
3. Execute `python main.py load_data` to batch import data from the ibd file to the database (Both input idb and `mysql_db_dir` should be available + connection availability)
4. wait for it to load the data into your new database

## With K8s

Checkout `k8s-sample.yaml` and changes value according to your needs (you will also need an active instance of the new database + Datadir access) and apply that in your cluster and exec into the newly created pod using `kubectl exec -it -n NAMESPACE po/PODNAME -- bash`

Also an alias added be make it easier to use called `mysql-db` use `mysql-idb` instead of `python main.py`

Other steps are like previous section

## With Docker

Bring up a container with both new and old data available (with connection access to new db) with image: `ghcr.io/anyongjin/mysql_idb:mysql-8.4` (change mysql version if needed)

Other steps are like previous section

# related question

**Schema mismatch (Clustered index validation failed. Because the .cfg file is missing, table definition of the IBD file could be different. Or the data file itself is already corrupted.)**

Occasionally this error occurs when importing ibd after mysql8. Use the ibd2sdi tool to generate sdi from the new table, and compare the old and new sdi files, which are basically the same. In the issues, a friend mentioned that the difference between the generated SQL and the original SQL might cause the table structure information to not match completely. He solved it by changing the statements that define primary keys and indexes from INDEX to KEY. There might also be other error situations, which could be considered as a direction: [#14](/../../issues/14).

**Bad start value for auto-increment column**

After importing data from the ibd file, the starting value of the auto-increment table is still 0, and an error would occur while inserting new data. You can use the following command to manually query and fix it:

```sql
select max(id) from `mytable`;
ALTER TABLE `mytable` AUTO_INCREMENT=val+1
```
