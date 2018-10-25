# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 00:01:59 2018

@author: David Veiga 
@github: https://github.com/davidaug
"""
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = FirefoxBinary('C:\Program Files\Mozilla Firefox')
driver = webdriver.Firefox(executable_path=r'C:\Drivers\geckodriver.exe')

driver.get('http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/BuscaEmpresaListada.aspx?idioma=pt-br')

time.sleep(10)

button = driver.find_element_by_name('ctl00$contentPlaceHolderConteudo$BuscaNomeEmpresa1$btnTodas')

button.click()

time.sleep(15)

companies = driver.find_element_by_id('ctl00_contentPlaceHolderConteudo_BuscaNomeEmpresa1_grdEmpresa')

root_soup = BeautifulSoup(companies.get_attribute('innerHTML'),'html.parser')

for link in root_soup.find_all('a', href=True)[:20:2]:
    codCVM = link['href'].split("=")[1]
    company_page = requests.get("http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp?CodCVM="+codCVM)

    if company_page.status_code == 200:
        c_soup = BeautifulSoup(company_page.content,'html.parser')
        table_info = c_soup.find('table', attrs={'class':'ficha'})
        rows = table_info.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            print
            if 'Nome de Pregão:' in cols[0].text:
                print(cols[1].text.strip())
            elif 'Site:' in cols[0].text:
                print(cols[1].text.strip())
            elif 'Classificação Setorial:' in cols[0].text:
                print(cols[1].text.strip())
            elif 'Atividade Principal:' in cols[0].text:
                print(cols[1].text.strip())
                
        time.sleep(10)
    
#    time.sleep(10)