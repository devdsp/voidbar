drop table users;
drop table accounts;
drop table items;
drop table journal;

create table users (identifier primary key,account_id);
create table accounts (
    id integer primary key autoincrement,
    balance,
    description
);
create table items (
    id integer primary key autoincrement, 
    identifier,
    value,
    description
);
create table journal(account_id,item_id,ammount,timestamp);

insert into items (identifier, value, description) values ('#$1',1,'cash monies');
insert into items (identifier, value, description) values ('#$2',2,'cash monies');
insert into items (identifier, value, description) values ('#$5',5,'cash monies');
insert into items (identifier, value, description) values ('#$10',10,'cash monies');
insert into items (identifier, value, description) values ('#$20',20,'cash monies');
insert into items (identifier, value, description) values ('#$50',50,'cash monies');
insert into items (identifier, value, description) values ('F4029764001807',-3.50,'ClubMate');

insert into accounts (id, balance, description) values(0,0,'Adam');
insert into users (identifier, account_id) values( '#devdsp',0);
insert into users (identifier, account_id) values( 'devdsp',0);
