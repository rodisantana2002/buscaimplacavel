# -*- coding: utf-8 -*-
# encoding: iso-8859-1

import re
import sys
import os
import logging
import csv
import time

from datetime import datetime
from googletrans import Translator

# log config
logging.basicConfig()
logger = logging.getLogger('Log.')
logger.setLevel(logging.DEBUG)

pathOrigem = '../files/convertidos/'
pathTraduzidos = '../files/traduzidos/'
pathPendentes = '../files/pendentes/'

class translate(object):

    def __init__(self):
        self.homeDir = "../logs"
        self.logFile = self.homeDir + '/translate.log'
        self.logger_handler = logging.FileHandler(self.logFile, mode='w')
        self.logger_handler.setLevel(logging.DEBUG)
        # Associe o Handler ao  Logger
        logger.addHandler(self.logger_handler)

        self.FIELD_NAMES = ['id',
                            'arquivo',
                            'tipo',
                            'txtorigem',
                            'txttranslate',
                            'datahoracarga', 
                            'datahoratranslate']

    def _popularDados(self, arquivoTXT):
        try:
            csv_file = "%s.csv" % os.path.basename(arquivoTXT)[0:-4]

            with open(pathPendentes + csv_file, 'w') as tmp:
                writer = csv.DictWriter(tmp, fieldnames=self.FIELD_NAMES)
                writer.writeheader()
                id = 1
                with open(arquivoTXT, 'r') as source:
                    for row in source:
                        data_hora_atuais = datetime.now()
                        data_atual = data_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')

                        if row[0:3] == '###' or row[0:3] == 'TIT' or row[0:3] == 'ABS' or row[0:3] == 'WOR' or row[0:3] == 'REF':
                            writer.writerow({'id':id,
                                            'arquivo':os.path.basename(arquivoTXT)[0:-4],
                                            'tipo': row[0:3],
                                            'txtorigem':row[3:].rstrip(),
                                            'txttranslate':'',
                                            'datahoracarga':data_atual,
                                            'datahoratranslate': ''
                                            })
                            id += 1

            return '---> {} ---[ ok ] Foram carregadas [{}] linhas com sucesso'.format(data_atual, id)

        except Exception:
            data_hora_atuais = datetime.now()
            data_atual = data_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')
            return '---> {} ---[erro] Arquivo não pode ser carregado'.format(data_atual)

    def _processarTraducao(self, arquivoCSV):
        try:
            csv_file = "%s.csv" % os.path.basename(arquivoCSV)[0:-4]

            id = 1
            with open(pathTraduzidos + csv_file, 'w') as tmp:
                writer = csv.DictWriter(tmp, fieldnames=self.FIELD_NAMES)
                writer.writeheader()

                with open(pathPendentes + csv_file, 'r') as arq:
                    reader = csv.DictReader(arq)
                    trans = Translator()

                    for row in reader:
                        data_hora_atuais = datetime.now()
                        data_atual = data_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')

                        if len(row['txtorigem'])==0 :
                            logger.debug('-----> linha em branco: [%s]', id)
                            txtTranslate = ''
                        elif row['tipo'] == 'REF':
                            logger.debug('-----> referências arq. [%s]', id)
                            txtTranslate = row['txtorigem']
                        else:    
                            txtTranslate = ''
                            logger.debug('-----> traduzindo texto [%s]', id)
                            txt = trans.translate(row['txtorigem'], dest='pt')
                            txtTranslate = txt.text                        
                                
                        writer.writerow({'id': row['id'],
                                        'arquivo': row['arquivo'],
                                        'tipo': row['tipo'],
                                        'txtorigem': row['txtorigem'].rstrip(),
                                        'txttranslate': txtTranslate,
                                        'datahoracarga': row['datahoracarga'],
                                        'datahoratranslate': data_atual
                                        })
                        id += 1
                        time.sleep(6)

            os.remove(pathPendentes+csv_file)
            return '---> {} ---[ ok ] Foram lidas [{}] linhas com sucesso'.format(data_atual, id)

        except Exception as exc:
            data_hora_atuais = datetime.now()
            data_atual = data_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')
            return '---> {} ---[erro] Arquivo não pode ser traduzido'.format(data_atual)


    def carregarRepositoriosCSV(self):
        logger.debug('----------------------------------------------------------------------------------------------')
        logger.debug('---> Iniciando processo de carga nos repositórios CSV.')
        logger.debug('----------------------------------------------------------------------------------------------')

        # Passo 01 carregar dos dados para os arquivos csv 
        arquivos = self._obterArquivos(pathOrigem, "txt")

        if len(arquivos) > 0:
            for arq in arquivos:
                logger.debug(self._popularDados(arq))

            logger.debug('----------------------------------------------------------------------------------------------')
            
        else:
            logger.debug('---> Não foram encontrados arquivos TXT para serem lidos')

    def traduzirArquivo(self):
        logger.debug('----------------------------------------------------------------------------------------------')
        logger.debug('---> Iniciando processo de tradução dos arquivos. (timer 6 seg.)')
        logger.debug('----------------------------------------------------------------------------------------------')

        # Passo 01 ler arquivos csv e processar tradução e atualização dos dados
        arquivos = self._obterArquivos(pathPendentes, "csv")

        if len(arquivos) > 0:
            for arq in arquivos:
                logger.debug('---> Processando tradução do arquivo [%s].', os.path.basename(arq)[0:-4])
                logger.debug(self._processarTraducao(arq))
            logger.debug('----------------------------------------------------------------------------------------------')

        else:
            logger.debug('---> Não foram encontrados arquivos CSV para serem traduzidos')

    def _obterArquivos(self, path, tipo):
        return ([path+file for p, _, files in os.walk(os.path.abspath(path)) for file in files if file.lower().endswith("." + tipo)])

def main():
    trans = translate()
    # trans.carregarRepositoriosCSV()
    trans.traduzirArquivo()

if __name__ == '__main__':
    main()

