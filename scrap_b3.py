# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 00:01:59 2018

@author: David Veiga 
@github: https://github.com/davidaug
"""
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup


binary = FirefoxBinary('C:\Program Files\Mozilla Firefox')
driver = webdriver.Firefox(executable_path=r'C:\Drivers\geckodriver.exe')
bt_all = "ctl00$contentPlaceHolderConteudo$BuscaNomeEmpresa1$btnTodas"
div_companies = "ctl00_contentPlaceHolderConteudo_BuscaNomeEmpresa1_grdEmpresa"

wait = WebDriverWait(driver,15)

driver.get('http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/BuscaEmpresaListada.aspx?idioma=pt-br')

wait.until(EC.element_to_be_clickable((By.NAME,bt_all)))

button = driver.find_element_by_name(bt_all)

button.click()

wait.until(EC.presence_of_element_located((By.ID,div_companies)))

companies = driver.find_element_by_id(div_companies)

root_soup = BeautifulSoup(companies.get_attribute('innerHTML'),'html.parser')

arr_companies = []

for link in root_soup.find_all('a', href=True)[::2]:
    
    
    dict_company = {"name":None,
                    "trading_name":None,
                    "site":None,
                    "classification":None,
                    "sector": None,
                    "subsector": None,
                    "segment": None,
                    "share_codes":None,
                    "common_shares":None,
                    "preffered_shares":None,
                    "cvm_code": None}
    
    codCVM = link['href'].split("=")[1]
    dict_company["cvm_code"] = codCVM
    
    company_page = requests.get("http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp?CodCVM="+codCVM)

    if company_page.status_code == 200:
        c_soup = BeautifulSoup(company_page.content,'html.parser')
        
        if link.text:
            dict_company['name'] = link.text
        # GENERAL INFO
        
        table_info = c_soup.find('table', attrs={'class':'ficha'})
        rows = table_info.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if cols:
                if 'Nome de Pregão:' in cols[0].text:
                    dict_company['trading_name'] = (cols[1].text.strip())
                elif 'Códigos de Negociação:' in cols[0].text:
                    cods = re.findall(r"\b[A-Z][0-Z][0-Z][0-Z][0-9]{1,2}\b",cols[1].text.strip())
                    if cods:
                        cods = list(dict.fromkeys(cods))
                        dict_company['share_codes'] = (cods)
                elif 'Site:' in cols[0].text:
                    dict_company['site'] = (cols[1].text.strip())
                elif 'Classificação Setorial:' in cols[0].text:
                    dict_company['classification'] = (cols[1].text.strip())
                    try:
                        classif_substring = cols[1].text.strip().split("/")
                        dict_company['sector'] = classif_substring[0].strip()
                        dict_company['subsector'] = classif_substring[1].strip()
                        dict_company['segment'] = classif_substring[2].strip()
                    except:
                        None
                    
                
        # SHARES INFO
        
        div_shares_info = c_soup.find('div', attrs={'id':'div1'})
        table_shares_info = div_shares_info.find('table')
        
        rows = table_shares_info.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if cols:
                if 'Quantidade de Ações Ordinárias' in cols[0].text:
                    dict_company['common_shares'] = int(cols[1].text.strip().replace(".",""))
                elif 'Quantidade de Ações Preferenciais' in cols[0].text:
                    dict_company['preffered_shares'] = int(cols[1].text.strip().replace(".",""))
            
        arr_companies.append(dict_company) 
    
        time.sleep(0.15)