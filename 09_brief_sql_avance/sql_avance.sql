EXPLAIN ANALYSE 
SELECT 
  sum(nb) 
FROM 
  entrepot.fait_etablissement 
WHERE 
  insee_code = '69123'; EXPLAIN ANALYSE 
SELECT 
  sum(nb) 
FROM 
  entrepot.fait_etablissement 
WHERE 
  type = 'lycee'; 
/*L'index de clé primaire sert dnas le premier cas car insee_code est la clé primaire; a contrario de type*/
CREATE INDEX 
  IF NOT EXISTS index_type ON entrepot.fait_etablissement(type); EXPLAIN ANALYSE 
SELECT 
  sum(nb) 
FROM 
  entrepot.fait_etablissement 
WHERE 
  type = 'lycee'; 
SELECT 
  indexname, 
  indexdef 
FROM 
  pg_indexes 
WHERE 
  schemaname = 'public' 
  AND tablename = 'entrepot.fait_etablissement'; 
DROP 
  FUNCTION IF EXISTS entrepot.top_commune(p_type text, p_n integer); 
CREATE FUNCTION 
  entrepot.top_commune(p_type text, p_n integer) returns TABLE(
    insee_code VARCHAR(5)
  ) language plpgsql as $$ begin RETURN query 
SELECT 
  fe.insee_code 
FROM 
    entrepot.fait_etablissement fe 
WHERE 
  type = p_type 
ORDER BY 
  nb DESC
LIMIT 
  p_n; end; $$; 
/*entrepot.habitants_par(p_type text) : par département, les habitants, le nombre d'établissements du type, et le ratio habitants par établissement.*/
DROP 
  FUNCTION IF EXISTS entrepot.habitants_par(p_type text); 
CREATE FUNCTION 
  entrepot.habitants_par(p_type text) returns TABLE(
    departement TEXT, habitants INTEGER, 
    nb_etab INTEGER, ratio_hab_etab INTEGER
  ) language plpgsql as $$ begin RETURN query 
SELECT 
  dc.departement, 
  SUM(population):: INTEGER, 
  SUM(nb):: INTEGER, 
  SUM(population):: INTEGER / SUM(nb):: INTEGER ratio 
FROM 
    entrepot.fait_etablissement 
  JOIN entrepot.dim_commune dc USING(insee_code) 
WHERE 
  type = p_type 
GROUP BY 
  dc.departement 
ORDER BY 
  dc.departement DESC; end; $$; 
SELECT 
  entrepot.top_commune('pharmacie', 5); 
SELECT 
  entrepot.habitants_par('pharmacie'); CREATE 
OR REPLACE FUNCTION prevent_delete() RETURNS TRIGGER AS $$ BEGIN 
  RAISE EXCEPTION 'DELETE sur une dimension d entrepot pas autorisé';
END; $$ LANGUAGE plpgsql; CREATE 
OR REPLACE TRIGGER prevent_delete_dim_commune BEFORE DELETE ON entrepot.dim_commune FOR EACH STATEMENT EXECUTE FUNCTION prevent_delete(); BEGIN 
  ; CREATE 
  OR REPLACE FUNCTION fun_update_warehouse_pharmacie() returns TRIGGER language plpgsql AS $$ BEGIN 
    INSERT INTO   entrepot.fait_etablissement(insee_code, type, nb) 
    VALUES 
      (NEW.insee_code, 'pharmacie', 1) ON CONFLICT(insee_code, type) DO 
    UPDATE 
    SET 
      nb =   entrepot.fait_etablissement.nb + 1; RETURN NEW;
  END; $$; CREATE 
  OR REPLACE TRIGGER update_warehouse_pharmacie 
  AFTER 
    INSERT ON pharmacie FOR EACH ROW EXECUTE FUNCTION fun_update_warehouse_pharmacie(); INSERT INTO pharmacie(finess, name, insee_code) 
  VALUES 
    (690123460, 'test', '46252'); 
  SELECT 
    * 
  FROM 
    entrepot.fait_etablissement 
  WHERE 
    insee_code = '46252'; INSERT INTO pharmacie(finess, name, insee_code) 
  VALUES 
    (690123461, 'test', '46252'); 
  SELECT 
    * 
  FROM 
    entrepot.fait_etablissement 
  WHERE 
    insee_code = '46252'; ROLLBACK; 
  /*Le nombre total de trigger necessaire avec cette methode serait: (nb opérations*nb_tables)-> 3*5=15 */
  /*la maintenance par trigger se justifie si il ya des petites modifications fréquentes sur la base de données et qu'il y a souvent besoin de faire des requêtes sur des 
  données à jour; dans ce cas la reconstruction régulière devient excessive et trop coûteuse*/
  EXPLAIN (ANALYZE, BUFFERS) 
  SELECT 
    sum(nb) 
  FROM 
    entrepot.fait_etablissement 
  WHERE 
    insee_code = '69123';
