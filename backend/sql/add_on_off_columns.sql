begin;

alter table public.advanced_stats
  add column if not exists off_rating_on_court numeric(8,3),
  add column if not exists off_rating_off_court numeric(8,3),
  add column if not exists def_rating_on_court numeric(8,3),
  add column if not exists def_rating_off_court numeric(8,3),
  add column if not exists net_rating_on_court numeric(8,3),
  add column if not exists net_rating_off_court numeric(8,3),
  add column if not exists off_rating_on_off_diff numeric(8,3),
  add column if not exists def_rating_on_off_diff numeric(8,3),
  add column if not exists net_rating_on_off_diff numeric(8,3);

commit;
