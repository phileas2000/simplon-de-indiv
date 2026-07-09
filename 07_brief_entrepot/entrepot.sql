/*grain table fait: etablissement('pharmacie','lycee','college','bibliotheque','equipement_sport')*/


CREATE TABLE IF NOT EXISTS dim_commune(insee_code VARCHAR(5) PRIMARY KEY,
    name TEXT,
    departement TEXT,
    region TEXT,
    population INTEGER);

CREATE TABLE IF NOT EXISTS dim_types(
    type TEXT PRIMARY KEY,
    libelle TEXT);

CREATE TABLE IF NOT EXISTS fait_etablissement(
    insee_code VARCHAR(5) PRIMARY KEY REFERENCES dim_commune (insee_code),
    type TEXT REFERENCES dim_types (type),
    nb INTEGER);

TRUNCATE TABLE fait_etablissement,dim_types,dim_commune;

INSERT INTO dim_commune 
    SELECT c.insee_code,c.name,d.name,r.name,c.population
    FROM commune c 
    JOIN departement d ON c.code_departement=d.code_departement
    JOIN region r ON d.code_region=r.code_region;

INSERT INTO dim_types(type,libelle) VALUES ('pharmacie','ph'),('lycee','ly'),('college','co'),('bibliotheque','bi'),('equipement_sport','eq');


INSERT INTO fait_etablissement(insee_code,type,nb)
SELECT insee_code,type,nb
FROM(
    SELECT ph.insee_code,'pharmacie'  type,COUNT(*) nb
    FROM pharmacie ph
    GROUP BY ph.insee_code
            
    UNION ALL
            
    SELECT c.insee_code,'college' AS type,COUNT(*)
    FROM college c
    GROUP BY c.insee_code
            
    UNION ALL
            
    SELECT l.insee_code,'lycee' AS type,COUNT(*)
    FROM lycee l
    GROUP BY l.insee_code
            
    UNION ALL
            
    SELECT b.insee_code,'bibliotheque' AS type,COUNT(*)
    FROM bibliotheque b
    GROUP BY b.insee_code
            
    UNION ALL
            
    SELECT eq.insee_code,'equipement_sport' AS type,COUNT(*)
    FROM equipement_sport eq
    GROUP BY eq.insee_code
)