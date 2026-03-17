drop view if exists vtar.yerevan_outages;

create view vtar.yerevan_outages as
select
    o.id,
    o.event_at,
    case o.kind
        when 'ENA' then 'Electricity'
        when 'VJUR' then 'Water'
    end as kind,
    initcap(a.canonical_hy) as address_hy,
    initcap(address_en) as address_en,
    o.building,
    vtar.normalize_building_cache_key(o.building) as building_key,
    o.consumer_count,
    o.scraped_at,
    g.building as geocode_building,
    g.latitude,
    g.longitude,
    g.source as geocode_source,
    g.confidence as geocode_confidence,
    g.district as geocode_district_hy,
    g.district_en as geocode_district_en,
    g.precision as geocode_precision,
    g.district_source as geocode_district_source,
    g.status as geocode_status,
    g.attempt_count as geocode_attempt_count,
    g.last_error as geocode_last_error,
    g.updated_at as geocode_updated_at
from vtar.outages as o
left join vtar.cities as c on c.id = o.city_id
left join vtar.addresses as a on a.id = o.address_id
left join vtar.geocode_cache as g
    on g.city_id = o.city_id
   and g.address_id = o.address_id
   and g.building = vtar.normalize_building_cache_key(o.building)
where o.city_id in (3, 2187);