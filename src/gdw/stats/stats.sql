CREATE USER test WITH PASSWORD 'test' CREATEDB;
CREATE DATABASE gites_wallons_test OWNER test;
create view blockinghistory as select heb_blockhistory_heb_pk as heb_pk, heb_blockhistory_blocked_dte as block_start, case when heb_blockhistory_activated_dte is null then current_date else heb_blockhistory_activated_dte end as block_end from heb_blocking_history;
