# IPv4 and IPv6 Invisible Resources

**Author**: carlos@lacnic.net AT Panama, 20191006

## Goal

Find all RIR assignments that are currently **NOT** visible in the routing table.

## Pipeline Description

El pipeline consta de 4 pasos y sería así:

```
STEP 0: generar el netdata.db (esto tiene su propio pipeline)
   script: s0_get_netdatadb
   salida: netdata-latest.db

STEP 1: tag assignments as visible / not visible
   script: s1_tag_resources
   salida: s1_tag_resources.csv
   formato: Prefix|VisibleOrNot

STEP 2: agregarle a cada línea el org-id:
   script: s2_enrich_with_orgid
   salida: s2_enrich_with_orgid.csv
   format: Prefix|VisibleOrNot|org-id

agrupar listado por org ids y generar un segundo listado por org ids con número de anuncios invalidados
   script: s3_group_by_orgid
```

## Publicación de resultados:

Los productos de este pipeline son:

*TBW

Están disponibles en:

*TBA

## Anexos

SQL útiles:

```
select orgid1,count(orgid1) as cnt from invalids group by orgid1 order by cnt asc;
```

```select orgid0,count(orgid0) as count, name,email1,email2 from invalids,registrados where orgid0=orgid group by orgid0 order by count asc;```


```
select orgid0,count,name,email1,email2 from (

select orgid0,count(orgid0) as count 

from invalids  group by orgid0 order by count asc),

registrados 

where orgid0=orgid group by orgid0 order by count asc;
```
