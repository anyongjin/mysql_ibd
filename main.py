#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File  : ibd2sql.py
# Author: anyongjin
# Date  : 2022/10/3
import json
import os
import subprocess
import platform
from typing import List, Dict
import logging
import pymysql

global ibd2sdi_path
ibd2sdi_path = None
logger = logging.getLogger("mysql_ibd")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("%(asctime)s %(process)d %(levelname)s %(message)s"))
logger.addHandler(ch)

fixed_def_names = {"CURRENT_TIMESTAMP", "LOCALTIMESTAMP", "UNIX_TIMESTAMP", "UTC_TIMESTAMP", "TIMESTAMP", "NOW", 
                   "CURRENT_DATE", "CURRENT_TIME", "CURDATE", "CURTIME"}

def is_fixed_def_name(name: str) -> bool:
    name = name.upper()
    for n in fixed_def_names:
        if name.startswith(n):
            return True
    return False


def ibd2sql(args: dict):
    global ibd2sdi_path
    if not ibd2sdi_path or not os.path.isfile(ibd2sdi_path):
        is_windows = platform.system() == "Windows"
        where_cmd = "where" if is_windows else "whereis"
        ibd2sdi_info = subprocess.run([where_cmd, "ibd2sdi"], stdout=subprocess.PIPE)
        if ibd2sdi_info.returncode != 0:
            raise FileNotFoundError("`ibd2sdi` path is invalid")
        ibd2sdi_path = ibd2sdi_info.stdout.decode("utf-8").strip()
        if not is_windows:
            res_arr = ibd2sdi_path.split(" ")
            if len(res_arr) <= 1:
                raise ValueError("no installed `ibd2sdi` found on system!")
            ibd2sdi_path = res_arr[1]
            if not os.path.isfile(ibd2sdi_path):
                raise FileNotFoundError(
                    f'ibd2sdi({ibd2sdi_path}) not exist, output: {
                        " ".join(res_arr)} '
                )
    db_name = os.path.basename(args["input_ibds"])
    ibd_names = [
        name for name in os.listdir(args["input_ibds"]) if name.endswith(".ibd")
    ]
    if not os.path.isdir(args["output"]):
        os.mkdir(args["output"])
    sdi_out = os.path.join(args["output"], db_name + "_sdi")
    if not os.path.isdir(sdi_out):
        os.mkdir(sdi_out)
    skip_tbls: list = args.get("skip_tbls", [])
    sql_path = os.path.join(args["output"], db_name + ".sql")
    builder = open(sql_path, "w", encoding="utf-8")
    only_tbls: list = args.get("only_tbls", [])
    include_drop: bool = args.get("include_drop", True)

    for ibd_name in ibd_names:
        tbl_name = ibd_name.rstrip(".ibd")
        if tbl_name in skip_tbls:
            continue
        if only_tbls and tbl_name not in only_tbls:
            continue
        logger.info(f"handle table: {ibd_name}")
        sdi_path = os.path.join(sdi_out, os.path.splitext(ibd_name)[0] + ".sdi")
        if not os.path.isfile(sdi_path):
            ibd_path = os.path.join(args["input_ibds"], ibd_name)
            sdi_result = subprocess.run(
                [ibd2sdi_path, "--dump-file=" + sdi_path, ibd_path],
                stdout=subprocess.PIPE,
            )
            if sdi_result.returncode != 0:
                raise ValueError(f"[{ibd_name}] ibd2sdi error:{sdi_result}")
        sdi_data: dict = json.load(open(sdi_path, "r", encoding="utf-8"))[1]["object"]
        if sdi_data.get("dd_object_type") != "Table":
            logger.warning(
                f'unsupported sdi type: {sdi_data.get("dd_object_type")} for {
                    ibd_name}'
            )
            continue
        dd_obj: dict = sdi_data.get("dd_object")
        columns: List[Dict] = dd_obj.get("columns")
        indexes: List[Dict] = dd_obj.get("indexes")
        out_tbl_name: str = dd_obj.get("name")
        out_tbl_engine: str = dd_obj.get("engine")
        if include_drop:
            builder.write(f"DROP TABLE IF EXISTS `{out_tbl_name}`;\n")
        builder.write(f"CREATE TABLE `{out_tbl_name}` (\n")
        is_first = True
        for col in columns:
            if col.get("hidden") == 2:
                continue
            if is_first:
                is_first = False
            else:
                builder.write(",\n")
            col_name = col.get("name")
            col_type = col.get("column_type_utf8")
            builder.write(f"\t`{col_name}` {col_type}")
            if not col.get("is_nullable"):
                builder.write(" NOT NULL")
            if col.get("is_auto_increment"):
                builder.write(" AUTO_INCREMENT")
            if not col.get("has_no_default"):
                if col.get("default_value_null"):
                    builder.write(" DEFAULT NULL")
                else:
                    def_val = col.get("default_value_utf8")
                    if def_val:
                        if is_fixed_def_name(def_val):
                            builder.write(f" DEFAULT {def_val}")
                        else:
                            builder.write(f" DEFAULT '{def_val}'")
            comment = col.get("comment")
            if comment:
                comment = comment.replace("'", "''")
                builder.write(f" COMMENT '{comment}'")
        for idx in indexes:
            if idx.get("hidden"):
                continue
            elts = idx.get("elements")
            if not elts:
                continue
            idx_name = idx.get("name")
            use_elts = [elt for elt in elts if elt["length"] < 4294967295]
            if not use_elts:
                logger.warn(
                    f"invalid index found, no columns linked: {
                        ibd_name}/{idx_name}"
                )
                continue
            builder.write(",\n\t")
            col_names = [columns[elt.get("column_opx")].get("name") for elt in use_elts]
            show_cols = ", ".join(f"`{name}`" for name in col_names)
            idx_type = idx.get("type")
            if idx_type == 1:
                builder.write(f"PRIMARY KEY ({show_cols})")
            elif idx_type in {2, 3}:
                builder.write(f"INDEX `{idx_name}` ({show_cols})")
            elif idx_type == 4:
                builder.write(f"FULLTEXT `{idx_name}` ({show_cols})")
            else:
                raise ValueError(
                    f"unsupport index type: {
                        idx_type} for {ibd_name}/{idx_name}"
                )
        builder.write(f"\n) ENGINE={out_tbl_engine};\n\n")
        builder.flush()
    builder.close()
    logger.info(f"sql generated at: {sql_path}")
    if args["apply_sql"]:
        logger.info("applying output to dest")
        with open(sql_path, "r") as outputfile:
            db_config = config["connection_info"]
            cursor = pymysql.connect(**db_config).cursor()
            cursor.executemany(outputfile.read(), ())


def link_tables_ibd(config: dict):
    import shutil

    db_config = config["connection_info"]
    cursor = pymysql.connect(**db_config).cursor()
    ibd_dir = config["input_ibds"]
    ibd_names = [name for name in os.listdir(ibd_dir) if name.endswith(".ibd")]
    skip_tbls: list = config.get("skip_tbls", [])
    mysql_out = config["mysql_db_dir"]
    skip_nonempty = config["skip_nonempty_tbl"]
    mismatch_tbls, mismatch_err = set(), None
    only_tbls: list = config.get("only_tbls", [])
    for ibd_name in ibd_names:
        tbl_name = os.path.splitext(ibd_name)[0]
        if tbl_name in skip_tbls:
            continue
        if only_tbls and tbl_name not in only_tbls:
            continue
        cursor.execute(f"SHOW TABLES LIKE '{tbl_name}';")
        tbl_res = cursor.fetchall()
        if not tbl_res:
            raise ValueError(f"table `{tbl_name}` not exist!")
        tbl_unlinked = False
        if skip_nonempty:
            try:
                cursor.execute(f"SELECT EXISTS (SELECT 1 FROM `{tbl_name})`;")
                row_num = cursor.fetchone()[0]
                if row_num > 0:
                    continue
            except pymysql.err.InternalError as e:
                if e.args[0] in {1812, 1814}:
                    tbl_unlinked = True
                else:
                    raise e
        ibd_path = os.path.join(ibd_dir, ibd_name)
        ibd_size = os.path.getsize(ibd_path)
        logger.info(f"importing table: {tbl_name}, size: {ibd_size}")
        if not tbl_unlinked:
            cursor.execute(f"ALTER TABLE `{tbl_name}` DISCARD TABLESPACE;")
        shutil.copy(ibd_path, os.path.join(mysql_out, ibd_name))
        try:
            cursor.execute(f"ALTER TABLE `{tbl_name}` IMPORT TABLESPACE;")
        except pymysql.err.InternalError as e:
            if e.args[0] == 1808:
                mismatch_tbls.add(tbl_name)
                mismatch_err = e
            else:
                raise e
    if mismatch_err:
        raise ValueError(
            f'schema mismatch tbls: {",".join(mismatch_tbls)}', mismatch_err
        )
    print("import complete!")


if __name__ == "__main__":
    import yaml
    import argparse

    parser = argparse.ArgumentParser(
        description="generate sql from ibd for mysql innodb engine, and import data from ibd automatically"  # noqa: E501
    )
    parser.add_argument(
        "-c",
        "--config",
        help="config.yaml file path",
        default=os.path.join(os.path.dirname(__file__), "config.yml"),
        dest="config",
    )
    subparsers = parser.add_subparsers(help="tosql|load_data", dest="cmd")
    sql_parser = subparsers.add_parser("tosql", help="generate sql from ibd files")
    load_parser = subparsers.add_parser(
        "load_data", help="load data from ibd for tables"
    )
    args = parser.parse_args()
    config_path = args.config
    config = yaml.safe_load(open(config_path, "r", encoding="utf-8"))
    command_mapping = {"tosql": ibd2sql, "load_data": link_tables_ibd}
    if args.cmd not in command_mapping.keys():
        raise ValueError(f"unsupported sub command: {args.cmd}")
    command_mapping[args.cmd](config)
