-- auto-generated definition
create table results
(
  uid          varchar(16) not null
    constraint results_pk
      primary key,
  thumbnail    varchar,
  link         varchar,
  title        varchar,
  price        integer,
  town         varchar,
  distance     integer,
  year         varchar,
  berth        integer,
  miles        integer,
  transmission varchar,
  seats        varchar,
  engine       varchar,
  extras       varchar,
  column_15    integer
);

alter table results
  owner to "david.lush";

create unique index results_uid_uindex
  on results (uid);

