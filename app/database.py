import sys
import sqlite3
import os
import logging
import csv

from sqlite3 import Error

# log config
logging.basicConfig()
logger = logging.getLogger('Log.')
logger.setLevel(logging.DEBUG)

class database(object):
    def __init__(self):
        self.pathOrigem = '../bases/database/bot.db'
        self.pathConvertido = '../bases/source.csv'

    def _getConn(self):
        try:
            conn = sqlite3.connect(self.pathOrigem)
            return conn
        except Error as e:
            logger.debug(e)
            return None
        return sqlite3.connect(self.pathOrigem)

    def _criarTabela(self, strSQL):
        cn = self._getConn()
        
        try:
            cursor = cn.cursor()
            cursor.execute(strSQL)
            logger.debug("tabela criada com sucesso")
        except Error as e:
            logger.debug(e)
        cn.close()

    def _gerarTabelas(self):
        tabelas = []
        tabelas.append("""CREATE TABLE Pesquisa (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                                                descricao VARCHAR(30), 
                                                situacao VARCHAR(20),
                                                criado_em VARCHAR(12));""")

        tabelas.append("""CREATE TABLE Artigo (id VARCHAR(50) NOT NULL PRIMARY KEY , 
                                               situacao VARCHAR(20),
                                               titulo TEXT, 
                                               ano VARCHAR(4), 
                                               autores TEXT, 
                                               resumo TEXT, 
                                               keywords TEXT, 
                                               doi TEXT, 
                                               url TEXT, 
                                               tipo_publicacao VARCHAR(30), 
                                               base_origem VARCHAR(20), 
                                               pesquisa_id INTEGER,
                                               criado_em VARCHAR(12));""")

        tabelas.append("""CREATE TABLE ArtigoElemento (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                                                       situacao VARCHAR(20),
                                                       txtorigem TEXT, 
                                                       txttranslate TEXT, 
                                                       tipo VARCHAR(3), 
                                                       artigo_id VARCHAR(50),
                                                       criado_em VARCHAR(12));""")

        tabelas.append("""CREATE TABLE Referencia (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                                                       identificador VARCHAR(10), 
                                                       descricao TEXT, 
                                                       artigo_id VARCHAR(50),
                                                       criado_em VARCHAR(12))""")

        for tabela in tabelas:
            self._criarTabela(tabela)

    def salvarArtigo(self):
        cn = self._getConn()
        # string insert
        strSQL_INSERT = """INSERT INTO Artigo (id,situacao,titulo,ano,autores,resumo,keywords,doi,url,tipo_publicacao,base_origem,pesquisa_id,criado_em)  
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        # string busca
        strSQL_BUSCAR = """SELECT id FROM Artigo WHERE id = ?"""                         

        try:
            cursor_reader = cn.cursor()
            with open(self.pathConvertido, 'r') as arq:
                reader = csv.DictReader(arq)
                cursor_reader = cn.cursor()
                for row in reader:                        
                        cursor_reader.execute(strSQL_BUSCAR, (row['id'],))
                        if cursor_reader.fetchall().__len__() == 0:
                            cursor_exec = cn.cursor()
                            artigo = [(row['id'], 
                                       row['situacao'],
                                       row['title'], 
                                       row['year'], 
                                       row['author'], 
                                       '', 
                                       row['keywords'], 
                                       row['doi'], 
                                       row['url'], 
                                       row['tipo'], 
                                       row['base'], 
                                       '', 
                                       '')]

                            cursor_exec.executemany(strSQL_INSERT, artigo)
                            cn.commit()
                            logger.debug("Artigos salvos com sucesso")
                        else:
                            logger.debug("Artigos já foi registrado")

        except Error as e:
            cn.rollback()
            logger.debug(e)
        cn.close()
                    

    def salvarArtigoElemento(self):
        pass    

    def salvarReferencias(self):
        pass    

    def _obterArquivos(self, path, tipo):
        return ([path+file for p, _, files in os.walk(os.path.abspath(path)) for file in files if file.lower().endswith("." + tipo)])

def main():
    db = database()
    # db._gerarTabelas()
    db.salvarArtigo()


if __name__ == '__main__':
    main()
