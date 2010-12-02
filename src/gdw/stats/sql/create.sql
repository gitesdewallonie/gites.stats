create table log (
    log_pk serial primary key,
    log_date timestamp not null,
    log_path varchar not null,
    log_hebid varchar,
    log_host varchar,
    log_agent varchar
);

create index log_date_idx on log(log_date);
create index log_date_path_idx on log(log_date, log_path);
