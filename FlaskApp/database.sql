create database pastebin;
use pastebin
create table users(
    id int auto_increment not null primary key,
    name varchar(255),
    password varchar(255),
    email varchar(255)
);

create table pastes(
    id int auto_increment not null primary key,
    url varchar(255),
    text varchar(255),
    author varchar(255)
);
