#!/usr/bin/env python
# -*- coding: utf-8 -*-

sqlstr = """
CREATE TABLE IF NOT EXISTS cache_control (
id int PRIMARY KEY auto_increment,
uuid VARCHAR(32) UNIQUE NOT NULL,
build_time datetime NOT NULL,
status VARCHAR(8) NOT NULL
) CHARSET utf8;
"""
sqlstr2 = """
CREATE TABLE IF NOT EXISTS blog (
id int PRIMARY KEY auto_increment,
uuid VARCHAR(32) UNIQUE NOT NULL,
title VARCHAR(32) NOT NULL,
build_time datetime NOT NULL,
status VARCHAR(8) NOT NULL,
info TEXT not NULL 
) CHARSET utf8;
"""
sqlstr3 = """
CREATE TABLE IF NOT EXISTS file (
id int PRIMARY KEY auto_increment,
uuid VARCHAR(32) UNIQUE NOT NULL,
file_path VARCHAR(128) NOT NULL,
build_time datetime NOT NULL,
status VARCHAR(8) NOT NULL
) CHARSET utf8;
"""