#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import sys
from collections import OrderedDict
from pdb import set_trace

from ulalib.ula_setting import *

__date__ = "22-11-2024"
__version__ = "0.3.0"
__author__ = "Marta Materni"

FORMA = 0
FORMAKEY = 1
LEMMA = 2
ETIMO = 3
LANG = 4
POS = 5
FUNCT = 6
MSD = 7
SIGLA = 8
#   0       1     2     3         4       5   6       7 
# aidier|aidier|lemma|etimo|fr.it.,XIV,h|ADJ|Adp|Masc,Plur,Acc,Cmp
# amasse|amasse|lemma|etimo|angl.,XIV,g|ADV|auxTens|Man,Dem,Pos,MWEs
# aidier|aidier
# amasse|amasse

# POS_MSD_CSV_PATH = "static/cfg/pos_msd.csv"
# path_err = "log/exportdata.ERR.log"
# logerr = Log("w").open(path_err, 1).log
"""
POS|pos_name|msd_name|attrs
NOUN|noun|gender|Masc,Fem,Neut
NOUN|noun|number|Sing,Plur
NOUN|noun|case|Nom,Acc

g|GRENOBLE|grenoble|XII
h|TOUR|tour|XII
p|PARIS|paris|XIII
v|VENEZIA|venezia|XIV

"""

DATE = [
    'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'X1', 'XII', 'XIII',
    'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
]


class ExportData(object):

    def __init__(self, exp_name):
        self.exp_name = exp_name
        self.pma_df = None
        self.head_msds = []

        self.pma_rows = []
 
        # lista delle sigle nel corpus
        self.head_sigls = []
        self.text_sigla = 'x'

        #sigle per esportazione
        self.head_locs = []
        self.val_locs = []
        self.head_dates = []
        self.rif_dates = []
        self.exp_sigls = []
        self.locjs = {}
        self.datejs = {}
        #attributi duplicati in un pos
        self.padup = {}

    def find_msd_name_lst(self, pos, attr):
        lst = []
        for row in self.pma_rows:
            if row[0] == pos and row[3] == attr:
                self.pos_name = row[1]
                lst.append(row[2])
        return lst

    def read_pos_msd_csv(self):
        try:
            f = open(POS_MSD_CSV_PATH)
        except Exception as e:
            sys.exit(e)
        reader = csv.reader(f, delimiter='|')
        next(reader)
        msd_lst = []
        self.pma_rows = []
        for row in reader:
            pos = row[0].lower()
            pos_name = row[1]
            msd_name = row[2]
            attrs = row[3].split(",")
            msd_lst.append(msd_name)
            for a in attrs:
                self.pma_rows.append([pos, pos_name, msd_name, a])
        f.close()
        self.head_msds = list(OrderedDict.fromkeys(msd_lst))
        try:
            self.head_msds.remove('')
        except ValueError:
            pass

    #file per l'sportazioe di sigle, date e località dei testimoni
    def read_exp_csv(self):
        rows = []
        try:
            with open(EXP_LOC_DAT_PATH, 'r', encoding=ENCODING) as f:
                reader = csv.reader(f, delimiter='|')
                for r in reader:
                    rows.append(r)
        except Exception as e:
            sys.exit(e)
        #set delle date
        ds = {r[3] for r in rows}
        # label head delle date
        self.head_dates = [f'DATE.{i}' for i in range(len(ds))]
        #date di riferimento per posizionamento date di riga
        self.rif_dates = [x for x in DATE if x in ds]
        for r in rows:
            sg = r[0]
            self.exp_sigls.append(sg)
            self.head_locs.append(r[1])
            self.val_locs.append(r[2])
            self.locjs[sg] = r[2]
            self.datejs[sg] = r[3]
        self.head_sigls = self.exp_sigls

    #attributi duplicati in un pos
    def pos_attrs_dupl(self, rows):
        js = {}
        for row in rows:
            pos = row[POS].lower()
            if pos not in js:
                js[pos] = {}
            attrs = row[MSD].split(',')
            for i, a in enumerate(attrs):
                if not a in js[pos]:
                    js[pos][a] = [i, i]
                    continue
                mm = js[pos][a]
                mi = min(i, mm[0])
                mx = max(i, mm[1])
                js[pos][a] = [mi, mx]
        # pajs = {}
        # for p in js:
        #     for a, mm in js[p].items():
        #         if mm[0] != mm[1]:
        #             if not p in pajs:
        #                 pajs[p] = {}
        #             pajs[p][a] = mm
        self.padup = js
        # for p in pajs.keys():
        #     print('\n', p)
        #     for a in pajs[p]:
        #         print(a, js[p][a])

    # località e date derivate dalla sigla itilizzando il file d copnfiurazione
    # venezia, ,paris, , XI,..XIV
    def sigl_to_loc_dat(self, sigls):
        #valopri loc di riga
        locs = [self.locjs[x] if x in sigls else '' for x in self.exp_sigls]
        #valori data di riga
        # set_trace()
        ds = {self.datejs[x] for x in sigls}
        dates = [x if x in ds else '' for x in self.rif_dates]
        row = locs + dates
        return row

    #distribuisce i valori di msd(li attrs)nelle colonne msd dell'esportazione
    def attrs_to_msd_columns(self, pos, attrs):
        columns_msd_vals = [''] * len(self.head_msds)
        for i, attr in enumerate(attrs):
            #controllare le righe trovate se > 1 vi sono attr duplicati
            rs = self.find_msd_name_lst(pos, attr)
            n = 0
            #esiste  attributo duplicato per il pos
            if len(rs) > 1:
                mm = self.padup[pos][attr]
                n = 1 if i > mm[0] else 0
            msd_name = rs[n]
            idx = self.head_msds.index(msd_name)
            columns_msd_vals[idx] = attr
        # print(self.exp_msd_columns)
        # print(pos, attrs)
        # print(columns_msd_vals, '\n')
        return columns_msd_vals

    # setta la riga per l'esportazione
    def build_row(self, row):
        pos = row[POS].lower()
        if pos == '':
            return None
        # print(SIGLA)
        # print(row)
        #sigle della riga
        sigls = row[SIGLA].split(',')
        sigls = [x for x in sigls if x != '']
        #distribuisce le sigle di riga nella lista delle sigle del corpus
        row_sigls = [x if x in sigls else '' for x in self.head_sigls]

        #attributi di riga escluso '
        row_attrs = row[MSD].split(',')
        row_attrs = [x for x in row_attrs if x != '']

        #assenazione valori attributi alle colonne msd
        row_msd_vals = self.attrs_to_msd_columns(pos, row_attrs)

        # separazione loc, data in  LANG
        l_d = f"{row[LANG]},,".split(',')
        lang = l_d[0]
        data = l_d[1]

        #aggiunta località e date testimone
        row_loc_dat = self.sigl_to_loc_dat(sigls)

        #["FORMA", "FORMAKEY,"LEMMA", "ETIMO", "LANG", "POS", "FUNCT"],MSDS,SIGLE ..,LOC,DATE..
        row_exp = [
            row[FORMA], row[FORMAKEY], row[LEMMA], row[ETIMO], lang, data,
            self.pos_name, row[FUNCT]
        ] + row_msd_vals + row_sigls + row_loc_dat
        return row_exp

    def export_corpus(self):
        #dict di pos_attr e lista msd nme  pos_msd.json
        self.read_pos_msd_csv()
        #tabella conversione sigla dta,loc
        self.read_exp_csv()

        corpus_path = os.path.join(CORPUS_DIR, CORPUS_NAME)
        rows = []
        # AAA sostituito csvr.reader 
        # try:
        #     with open(corpus_path, 'r', encoding=ENCODING) as f:
        #         reader = csv.reader(f, delimiter='|')
        #         for row in reader:
        #             rows.append(row)
        # except Exception as e:
        #     sys.exit(e)
        try:
            with open(corpus_path, 'r', encoding=ENCODING) as f:
                for line in f:
                    if(len(line.strip())==0):
                        continue
                    row = line.strip().split('|')
                    rows.append(row)
        except Exception as e:
            sys.exit(e)

        exp_name = f"dictionary.{self.exp_name}.csv"
        exp_path = os.path.join(DATA_EXPORT_DIR, exp_name)
        print(os.linesep)
        print(exp_path)
        self.pos_attrs_dupl(rows)
        # #lista sigle di tutto il corpus
        # self.set_head_sigls(rows)
        # #dict di pos_attr e lista msd nme  pos_msd.json
        # self.read_pos_msd_csv()
        # #tabella conversione sigla dta,loc
        # self.read_exp_csv()

        try:
            fw = open(exp_path, "w", encoding=ENCODING)
            writer = csv.writer(fw, delimiter='|')

            # HEAD
            head = [
                "FORMA", "KEY", "LEMMA", "ETIMO", "LANG", "DATE", "POS",
                "FUNCT"
            ] + self.head_msds + self.head_sigls + self.head_locs + self.head_dates
            writer.writerow(head)
            #scrittura rows
            rows.sort()
            for row in rows:
                r = self.build_row(row)
                if r is None:
                    continue
                writer.writerow(r)
            fw.close()
            os.chmod(exp_path, 0o777)
        except IOError as e:
            msg = f'ERROR export_corpus: \n{e}\n'
            sys.exit(msg)
  
  
    def export_token(self, text_path):
        try:
            text_name = os.path.basename(text_path)
            token_name = text_name.replace(".txt", ".token.csv")
            token_path = os.path.join(DATA_DIR, token_name)
            exp_name = text_name.replace(".txt", f".{self.exp_name}.csv")
            exp_path = os.path.join(DATA_EXPORT_DIR, exp_name)
            print(exp_path)

            with open(token_path, 'r', encoding=ENCODING) as f:
                rows = []
                for line in f:
                    row = line.strip().split('|')
                    rows.append(row)

            with open(exp_path, 'w', encoding=ENCODING) as fw:
                head = ["FORMA", "KEY", "SIGL"]
                s="|".join(head)
                fw.write(s)
                fw.write(os.linesep)
                for row in rows:
                    row.append(self.text_sigla)
                    s="|".join(row)
                    fw.write(s)
                    fw.write(os.linesep)            
        except Exception as e:
            msg = f"ERROR export_token() \n{e}"
            sys.exit(msg)

    def export_token_list(self, names):
        token_names = [f'{x}.ula.csv' for x in names]
        data = os.linesep.join(token_names)
        exp_path = os.path.join(DATA_EXPORT_DIR, "token_list.txt")
        try:
            fw = open(exp_path, "w", encoding=ENCODING)
            fw.write(data)
            fw.close()
            os.chmod(exp_path, 0o777)
        except IOError as e:
            msg = f'ERROR exp_token_list()  \n{e}\n'
            sys.exit(msg)

    def read_text_list(self):
        try:
            with open(TEXT_LIST_PATH, 'r', encoding=ENCODING) as f:
                lst = f.readlines()
        except Exception as e:
            msg = f'ERROR read_text_lst \n{e}\n'
            sys.exit(msg)
        names = [x.strip() for x in lst]
        return names

    def export_data(self):
        names = self.read_text_list()
        self.export_token_list(names)
        for name in names:
            if name.strip() == '':
                continue            
            # self.text_sigla = name.split('.')[-1:][0]
            # XXX modificata sigla            
            n=name.replace(".","_")
            self.text_sigla = n.split('_')[-1:][0]
            text_name = name + ".txt"
            self.export_token(text_name)
        self.export_corpus()


def do_main(corpus_export_name="ula"):
    exportdata = ExportData(corpus_export_name)
    exportdata.export_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    print(f"\nauthor: {__author__}")
    print(f"release: {__version__} { __date__}\n")
    parser.add_argument('-n',
                        dest="name",
                        required=False,
                        default="ula",
                        metavar="",
                        help="-n <corpus_name> (default ula)")
    args = parser.parse_args()
    do_main(args.name)


"""

do_main
  └─ ExportData(corpus_export_name)
  └─ exportdata.export_data()
      └─ read_text_list()
      └─ export_token_list(names)
      └─ export_token(text_name)
          └─ read_pos_msd_csv()
          └─ read_exp_csv()
          └─ pos_attrs_dupl(rows)
          └─ build_row(row)
              └─ attrs_to_msd_columns(pos, attrs)
                  └─ find_msd_name_lst(pos, attr)
              └─ sigl_to_loc_dat(sigls)
      └─ export_corpus()

1. **`do_main`**:

2. **`export_data`**:
   - Chiama `read_text_list()` per leggere la lista dei file di testo.
   - Chiama `export_token_list(names)` per esportare la lista dei token.
   - Itera sui nomi dei file di testo e per ciascuno:
     - Chiama `export_token(text_name)` per esportare i token del testo.
   - Chiama `export_corpus()` per esportare il corpus.

3. **`read_text_list`**:
   - Legge la lista dei file di testo da un file specificato.

4. **`export_token_list`**:
   - Crea un file di testo contenente la lista dei nomi dei file di token.

5. **`export_token`**:
   - Legge il file di token CSV.
   - Aggiunge una colonna con la sigla del testo.
   - Scrive il risultato in un nuovo file CSV.

6. **`export_corpus`**:
   - Chiama `read_pos_msd_csv()` per leggere il file CSV delle parti del discorso e degli attributi MSD.
   - Chiama `read_exp_csv()` per leggere il file CSV delle sigle, date e località dei testimoni.
   - Legge il file del corpus CSV.
   - Chiama `pos_attrs_dupl(rows)` per trovare gli attributi duplicati nelle parti del discorso.
   - Itera sulle righe del corpus e per ciascuna:
     - Chiama `build_row(row)` per costruire la riga per l'esportazione.
   - Scrive il risultato in un nuovo file CSV.

7. **`read_pos_msd_csv`**:
   - Legge il file CSV delle parti del discorso e degli attributi MSD.
   - Memorizza le righe in `self.pma_rows`.
   - Crea `self.head_msds` per memorizzare i nomi degli attributi MSD.

8. **`read_exp_csv`**:
   - Legge il file CSV delle sigle, date e località dei testimoni.
   - Memorizza le informazioni in vari attributi della classe.

9. **`pos_attrs_dupl`**:
   - Trova gli attributi duplicati nelle parti del discorso.

10. **`build_row`**:
    - Costruisce una riga per l'esportazione del corpus.
    - Chiama `attrs_to_msd_columns(pos, attrs)` per distribuire i valori degli attributi MSD nelle colonne appropriate.
    - Chiama `sigl_to_loc_dat(sigls)` per ottenere le località e le date derivate dalle sigle.

11. **`attrs_to_msd_columns`**:
    - Distribuisce i valori degli attributi MSD nelle colonne appropriate.
    - Chiama `find_msd_name_lst(pos, attr)` per trovare le righe con i nomi degli attributi MSD selezionati.

12. **`find_msd_name_lst`**:
    - Trova le righe con i nomi degli attributi MSD selezionati.

13. **`sigl_to_loc_dat`**:
    - Ottiene le località e le date derivate dalle sigle.

"""