# Avec la syntaxe from ... import ... on import un seul  objet
from retriever import Retriever
from processor import Processor
from alerter import Alerter
import os
import sqlite3


# Avec la syntaxe import .... on import tout le package
import datetime

# Avec la syntaxe from ... import * on importe tout  🚨🚨 a ne pas utiliser
# risque de conflit avec un autre objet (fonction, class, variable)
# qui aurait le même nom
# ici pas de risque : seulement une fonction nommée time_exec
from time_exec import *


def get_structure(obj):
    if isinstance(obj, dict):
        return {k: get_structure(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [get_structure(obj[0])] if obj else []
    else:
        return type(obj).__name__

def main():
    starting_time = datetime.datetime.now()
    conn=sqlite3.connect("will_of_d.db")
    cur=conn.cursor()
    


    pirates_url = "http://www.volonte-d.com/perso/pirates.php"
    perso_url="http://www.volonte-d.com/perso"
    techniques_url="http://www.volonte-d.com/techniques/"
    retriever_instance = Retriever(url=pirates_url)
    ps = retriever_instance.get_page_source()
    processor_instance = Processor(text=ps)
    list_name_teams,list_href_teams = processor_instance.extract_teams_and_urls()

    team_crew_dict={}
    crew_tech_dict={}
    for name_team,href_team in zip(list_name_teams,list_href_teams):
        list_crew_names,list_crew_href = processor_instance.get_crew_from_href(href_team,perso_url)
        team_crew_dict[name_team]={"list_crew_names":list_crew_names,"list_crew_href":list_crew_href}
        for crew_href,crew_name in zip(list_crew_href,list_crew_names):
            techniques_dict=processor_instance.get_techniques_from_crew(crew_href,techniques_url )
            crew_tech_dict[crew_name]=techniques_dict
    print(get_structure(crew_tech_dict))
    alerter = Alerter()
    #alerter.alert("\n".join(list_name_teams))
    print("__________________________________________")
    #alerter.alert("\n".join(crew_tech_dict.keys()))
    #alerter.alert(crew_tech_dict)
    ending_time = datetime.datetime.now()
    time_exec(starting_time, ending_time)

    create_tables(cur)
    insert_into_tables(cur,list_name_teams,team_crew_dict,crew_tech_dict)
    check_tables(cur)
    conn.commit()
    cur.close()
    conn.close()

def create_tables(cur):
    cur.execute("DROP TABLE IF EXISTS teams ")
    query="""CREATE TABLE teams(
    name TEXT PRIMARY KEY
    )"""
    cur.execute(query)

    cur.execute("DROP TABLE IF EXISTS crews ")
    query="""CREATE TABLE crews(
    name TEXT PRIMARY KEY,
    team_name TEXT REFERENCES teams(name)
    )"""
    cur.execute(query)

    cur.execute("DROP TABLE IF EXISTS techniques ")
    query="""CREATE TABLE techniques(
    id INTEGER PRIMARY KEY,
    name TEXT,
    crew_name TEXT REFERENCES crews(name),
    img_technique BLOB
    )"""
    cur.execute(query)
    


def insert_into_tables(cur,list_name_teams,team_crew_dict,crew_tech_dict):
    print("ICI")
    
    insert_list_name_teams=[(name_team,) for name_team in list_name_teams]
    cur.executemany("INSERT INTO teams(name) VALUES (?)",insert_list_name_teams)

    crew_team_list= [(crew, team)
            for team in team_crew_dict.keys()
            for crew in team_crew_dict[team]["list_crew_names"]

    ]
    print("crew_team_list : "+str(crew_team_list))
    cur.executemany("INSERT INTO crews(name,team_name) VALUES (?,?)",crew_team_list)


    tech_crew_list=[(tech,img_tech,crew) for crew,techs_dict in crew_tech_dict.items() for tech,img_tech in zip(techs_dict["name"],techs_dict["img"])]
    print(get_structure(tech_crew_list))
    #print(" tech_crew_list : "+str( tech_crew_list))
    #print("tech_crew_listt: "+str([tech_crew_list[crew_name]["name"] for crew_name in tech_crew_list.keys()]))
    cur.executemany("INSERT INTO techniques(name,img_technique,crew_name) VALUES (?,?,?)",tech_crew_list)
  

def check_tables(cur):
    print("FETCHING FROM TABLES")
    cur.execute("SELECT * FROM teams LIMIT 5")
    print(cur.fetchall())
    cur.execute("SELECT * FROM crews LIMIT 5")
    print(cur.fetchall())
    cur.execute("SELECT * FROM techniques LIMIT 1")
    print(cur.fetchall())

if __name__ == "__main__":
    main()
