-- Ensure MySQL system tables exist
CREATE DATABASE IF NOT EXISTS mysql;

-- Ensure privilege tables are created
USE mysql;
SOURCE /usr/share/mysql/mysql_system_tables.sql;

-- Ensure root user exists and has proper permissions
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'rootpassword';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
