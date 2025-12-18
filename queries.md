# Part 1 : Sanity check
## Total number of lines
```sql
SELECT COUNT(*)
FROM scene
LEFT JOIN location
ON scene.id_location = location.id_location
LEFT JOIN worktitle
ON scene.id_title = worktitle.id_title
LEFT JOIN filmingtype
ON scene.id_filming_type = filmingtype.id_filming_type
LEFT JOIN adress_scene
ON scene.id_scene = adress_scene.id_scene
LEFT JOIN adress
ON adress_scene.id_adress = adress.id_adress
LEFT JOIN scene_realisator
ON scene.id_scene = scene_realisator.id_scene
LEFT JOIN realisator
ON scene_realisator.id_realisator = realisator.id_realisator
LEFT JOIN scene_productor
ON scene.id_scene = scene_productor.id_scene
LEFT JOIN productor
ON scene_productor.id_productor = productor.id_productor
```

## Total number of duplicates
My script removes duplicates so we can't know the amount of duplicates

## Total number of NULL/empty values for a column
```SQL
SELECT 
	SUM(CASE WHEN realisator.realisator IS NULL OR realisator.realisator = '' THEN 1 ELSE 0 END) AS realisatorEmpty 
FROM scene
LEFT JOIN location
ON scene.id_location = location.id_location
LEFT JOIN worktitle
ON scene.id_title = worktitle.id_title
LEFT JOIN filmingtype
ON scene.id_filming_type = filmingtype.id_filming_type
LEFT JOIN adress_scene
ON scene.id_scene = adress_scene.id_scene
LEFT JOIN adress
ON adress_scene.id_adress = adress.id_adress
LEFT JOIN scene_realisator
ON scene.id_scene = scene_realisator.id_scene
LEFT JOIN realisator
ON scene_realisator.id_realisator = realisator.id_realisator
LEFT JOIN scene_productor
ON scene.id_scene = scene_productor.id_scene
LEFT JOIN productor
ON scene_productor.id_productor = productor.id_productor
```

# Part 2 : Coherence of dates

## End of filming before the beginning
```SQL
SELECT *
FROM scene
WHERE scene.endDate < scene.startDate
```

## How many scenes per year
```SQL
SELECT yearFilming, COUNT(*) as ScenesByYear
FROM scene
GROUP BY scene.yearFilming
```

## Duration of filming
```SQL
SELECT scene.id_scene, worktitle.title, DATEDIFF(endDate, startDate) as FilmingDay
FROM scene
JOIN worktitle
ON scene.id_title = worktitle.id_title
WHERE endDate > startDate
```

# Part 3 : Stats

## Best district
```SQL
SELECT adress.postal_code, COUNT(adress.postal_code) as topDistrict
FROM scene
JOIN adress_scene
ON scene.id_scene = adress_scene.id_scene
JOIN adress
ON adress_scene.id_adress = adress.id_adress
GROUP BY adress.postal_code 
ORDER BY topDistrict DESC
```

## Best filming type
```SQL
SELECT filmingtype.type, COUNT(scene.id_filming_type) as typeFilming
FROM scene
JOIN filmingtype
ON scene.id_filming_type = filmingtype.id_filming_type
GROUP BY filmingtype.type
ORDER BY typeFilming DESC
```

## Best productors
```SQL
SELECT productor.productor, COUNT(scene_productor.id_productor) as bestProductor
FROM scene
JOIN scene_productor
ON scene.id_scene = scene_productor.id_scene
JOIN productor
ON scene_productor.id_productor = productor.id_productor
GROUP BY scene_productor.id_productor
ORDER BY bestProductor DESC
```

## Best films
```SQL
SELECT worktitle.title, COUNT(scene.id_title) AS bestTitle
FROM scene
JOIN worktitle
ON scene.id_title = worktitle.id_title
GROUP BY scene.id_title
ORDER BY bestTitle DESC
```

# Part 4 : Text quality

## Field with too much space between words
This problem is already manage by the script.

## Similar values
This problem is manage if the case of the words is different.

# Part 5 : Coordinates

## Empty coordinates
This problem is already manage by the script

## Coordinates not in Paris
```SQL
SELECT *
FROM Location 
WHERE 
    CAST(geopoint_2d->'$.latitude' AS DECIMAL(10, 7)) NOT BETWEEN 48.8 AND 48.9
    OR 
    CAST(geopoint_2d->'$.longitude' AS DECIMAL(10, 7)) NOT BETWEEN 2.25 AND 2.42;
```
## Impossible coordinates
```SQL
SELECT * FROM Location 
WHERE 
    CAST(geopoint_2d->'$.latitude' AS DECIMAL(10, 7)) < -90 
    OR CAST(geopoint_2d->'$.latitude' AS DECIMAL(10, 7)) > 90
    OR CAST(geopoint_2d->'$.longitude' AS DECIMAL(10, 7)) < -180 
    OR CAST(geopoint_2d->'$.longitude' AS DECIMAL(10, 7)) > 180;
```

# Part 6 : Functional queries

## Search an adress with rue de la paix
```SQL
SELECT adress.adress
FROM adress
WHERE adress.adress LIKE '%rue de la paix%'
```

## Search a scene filming during a period
```SQL
SET @startPeriod = '2016-03-25';
SET @endPeriod = '2018-05-26';

SELECT worktitle.title, scene.startDate, scene.endDate
FROM scene
JOIN worktitle
ON scene.id_title = worktitle.id_title
WHERE scene.startDate BETWEEN @startPeriod AND @endPeriod
```

## Search a scene filming on a date
```SQL
SELECT worktitle.title, scene.startDate, scene.endDate
FROM scene
JOIN worktitle
ON scene.id_title = worktitle.id_title
WHERE '2016-03-25' BETWEEN scene.startDate AND scene.endDate
```

# Part 7 : Theory

## What is a top query ?
A top query select only the x first values.
For example :
```SQL
SELECT adress.postal_code, COUNT(adress.postal_code) as topDistrict
FROM scene
JOIN adress_scene
ON scene.id_scene = adress_scene.id_scene
JOIN adress
ON adress_scene.id_adress = adress.id_adress
GROUP BY adress.postal_code 
ORDER BY topDistrict DESC
LIMIT 3
```
Only select the three first top district