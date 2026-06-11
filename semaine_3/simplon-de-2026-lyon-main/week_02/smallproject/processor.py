from bs4 import BeautifulSoup
import requests
from pathlib import Path

class Processor:
    def __init__(self, text):
        self.text = text

    def extract_teams_and_urls(self):
        soup = BeautifulSoup(
            self.text, "html.parser"
        )  
        tome_66= soup.find(class_="blockCache3")
        text_landmark = tome_66.find(string="Pirates de la Nouvelle Vague")
        table_nouvelle_vague = text_landmark.find_next("table") 
        a_list=table_nouvelle_vague.find_all("a")
        list_href_teams=[]
        list_name_teams=[]
        for a in a_list:
            list_href_teams.append(a["href"])
            list_name_teams.append(a.find_next("b").get_text())
        return list_name_teams,list_href_teams

    def get_crew_from_href(self,href,base_url):
        crew_list=[]
        crew_href_list=[]

        full_url=base_url+"/"+href
        content=requests.get(full_url)
        page_crew=BeautifulSoup(content.text,features="html.parser")

        if href=="paille.php":#retire element supposés être cachés imageAffiche1
            to_decompose=page_crew.find_all(class_="imageAffiche1")
            for element in to_decompose:
                element.decompose()
        
        page_trsbas0=page_crew.find_all("td",class_="trsbas0")
        for crew in page_trsbas0:
            b_tag=crew.find(lambda tag: tag.name=="b")
            if b_tag:
                crew_list.append(b_tag.get_text())

        page_trsbas=page_crew.find_all("td",class_="trsbas")
        for crew in page_trsbas:
            b_tag=crew.find(lambda tag: tag.name=="a")
            if b_tag:
                if b_tag.has_attr("href"):
                    crew_href_list.append(b_tag["href"])
        return crew_list,crew_href_list
    
    

    def get_techniques_from_crew(self,href,base_url):
        techniques_dict={"name":[],"img":[]}
        technique_url=base_url+href
        content=requests.get(technique_url)
        page=BeautifulSoup(content.text,features="html.parser")

        techniques_dict["name"].extend([b.get_text() for b in page.find_all("b")])

        images_techniques=[]
        tech_images_src= [img["src"] for td in page.find_all("td", class_="trsbas") if (img := td.find("img"))]
        for img_src in tech_images_src:
            if img_src ==None:
                continue
            try:
                with open('file.png', 'wb') as f:
                    img_content=requests.get(str(base_url)+"/"+str(img_src)).content
                techniques_dict["img"].append(img_content)
            except Exception as e:
                print(e)

        technique_url=base_url+href.replace(".php","2.php")
        try:
            content=requests.get(technique_url)
        except:
            pass
        else:
            page=BeautifulSoup(content.text,features="html.parser")
            techniques_dict["name"].extend([b.get_text() for b in page.find_all("b")])

            tech_images_src=[img["src"] for td in page.find_all("td", class_="trsbas") if (img := td.find("img"))]

            for img_src in tech_images_src:
                if img_src ==None:
                    continue
                try:
                    with open('file.png', 'wb') as f:
                        img_content=requests.get(str(base_url)+"/"+str(img_src)).content
                    techniques_dict["img"].extend(img_content)
                except Exception as e:
                    print(e)
        #print(techniques_dict)
        print("")
        return techniques_dict