/*le classement des départements par nombre de pharmacies*/
SELECT c.departement,SUM(e.nb) sum
            FROM dim_commune c 
            JOIN fait_etablissement e ON c.insee_code=e.insee_code 
            WHERE e.type='pharmacie' 
            GROUP BY c.departement
            ORDER BY sum;
/*la population par région et par département*/
SELECT c.region,c.departement,SUM(c.population) FROM dim_commune c GROUP BY ROLLUP(c.region,c.departement);
/*un classement des départements par densité de l'un des services.*/
SELECT c.departement,ROUND(SUM(e.nb)::numeric/SUM(c.population),6) densite
            FROM dim_commune c
            JOIN fait_etablissement e ON c.insee_code=e.insee_code
            WHERE e.type='college'
            GROUP BY c.departement
            ORDER BY densite DESC;
