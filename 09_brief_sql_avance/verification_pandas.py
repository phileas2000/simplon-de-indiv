import psycopg2
import pandas as pd

conn=psycopg2.connect(password="jaune2000",user="postgres",port="5432",host="localhost",database="megabase0")
cur=conn.cursor()
conn.autocommit=True

df_dim_commune=pd.read_sql("SELECT * FROM dim_commune",conn)
df_fait_etablissement=pd.read_sql("SELECT * FROM fait_etablissement",conn)

df_merged=df_dim_commune.merge(right=df_fait_etablissement,on="insee_code")
df_merged_by_dep_type=df_merged[["population","nb","region","type","departement"]].groupby(by=["departement","type","region"]).sum()

df_merged_by_dep_type=df_merged_by_dep_type.reset_index()
df_pivoted=df_merged_by_dep_type.pivot(index="departement",values="nb",columns="type")
df_pivoted.columns=df_pivoted.columns.set_names("nb_per_type")

query="""SELECT d0.name,
            (SELECT COUNT(*) FROM bibliotheque b 
            JOIN commune c USING(insee_code) 
            WHERE c.code_departement= d0.code_departement
            GROUP BY code_departement) 
            bibliotheque,
            (SELECT COUNT(*) FROM college co
            JOIN commune c USING(insee_code) 
            WHERE c.code_departement= d0.code_departement
            GROUP BY code_departement) 
            college,
            (SELECT COUNT(*) FROM equipement_sport eq
            JOIN commune c USING(insee_code) 
            WHERE c.code_departement= d0.code_departement
            GROUP BY code_departement) 
            equipement_sport,
            (SELECT COUNT(*) FROM lycee l
            JOIN commune c USING(insee_code) 
            WHERE c.code_departement= d0.code_departement
            GROUP BY code_departement) 
            lycee,
            (SELECT COUNT(*) FROM pharmacie p
            JOIN commune c USING(insee_code) 
            WHERE c.code_departement= d0.code_departement
            GROUP BY code_departement) 
            pharmacie
            FROM departement d0
            ORDER BY d0.name COLLATE "C"
            """
df_query=pd.read_sql(query,conn,index_col="name")

df_query.columns=df_query.columns.set_names("nb_per_type")
df_query.index=df_query.index.set_names("departement")


print(pd.testing.assert_frame_equal(df_query,df_pivoted))