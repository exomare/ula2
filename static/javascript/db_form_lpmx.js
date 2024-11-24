/** @format */

const ULA_DATA_DIR = `/ula_data`;
const DATA_DIR = `${ULA_DATA_DIR}/data`;
const URL_TEXT_LIST = `${ULA_DATA_DIR}/data/text_list.txt`;
const URL_CORPUS_OMOGR = `${ULA_DATA_DIR}/data_corpus/corpus_omogr.json`;
// let ALPHABETIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàèéìòù";
// let NUMERIC = "0123456789";
// var ULACHARSET = ALPHABETIC + NUMERIC;
var UAPUNCTS = `,.;::?!^~()[]{}<>=+-*#@£&%/«»“‘’"\`'`;

//key corpus con formkey duplicate
const KEY_OMOGR = "ula_omogr";

// key nome testo nello store
const KEY_TEXT_NAME = "ula_text_name";

// key nome dati
const KEY_DATA = "ula_data";
const KEY_DATA_FORM = "ula_form";
const KEY_DATA_TOKEN = "ula_token";

function clearWnd(txt) {
  return txt.replace(/\r/g, "");
}

var DbFormLpmx = {
  text_name: null,
  token_file: null,
  form_file: null,
  token_lst: null,
  form_lst: [],
  omogr_json: {},
  // lunghezza righe di testo e terminatore di riga
  len_row: 80,
  row_eof: "##",
  rows_js: [],
  get_text_name: function () {
    const store_text_name = localStorage.getItem(KEY_TEXT_NAME);
    const text_name = store_text_name || "";
    return text_name;
  },
  set_text_name: function (text_name) {
    this.text_name = text_name;
    this.token_file = `${text_name}.token.csv`;
    this.form_file = `${text_name}.form.csv`;
  },
  get_sigla: function (text_name) {
    //HACK gestione sigla
    // console.log("text_name:", text_name);
    const s = text_name.split("_");
    if (s.length > 1) {
      let x = s.slice(-1)[0];
      // console.log("sigla:", x);
      return x;
    }
    return text_name;
  },
  load_text_list: async function () {
    const url = URL_TEXT_LIST;
    let rows = [];
    const resp = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      cache: "no-store",
    });
    if (resp.ok) {
      const csv_data = await resp.text();
      //HACK rows = csv_data.trim().split("\n");
      const s = clearWnd(csv_data.trim());
      rows = s.split("\n");
    } else {
      alert(`${url} Not Found. `);
      rows = [];
    }
    return rows;
  },
  get_store: function () {
    let ok = false;
    const sf = localStorage.getItem(KEY_DATA_FORM);
    if (sf) {
      //HACK let lst = sf.trim().split("\n");
      const s = clearWnd(sf.trim());
      let lst = s.split("\n");
      // console.log("sf lst", lst.slice(0, 10));

      this.form_lst = lst.map((x) => x.split("|"));
      const st = localStorage.getItem(KEY_DATA_TOKEN);
      if (st) {
        // HACK lst = st.trim().split("\n");
        const s = clearWnd(st.trim());
        let lst = s.split("\n");
        // console.log("s lstf", lst.slice(0, 10));

        this.token_lst = lst.map((x) => x.split("|"));
        this.sort_form_lst();
        const so = localStorage.getItem(KEY_OMOGR);
        if (so) this.omogr_json = JSON.parse(so);
        else this.omogr_json = {};
        ok = true;
      }
    }
    return ok;
  },
  set_store: function () {
    try {
      localStorage.setItem(KEY_TEXT_NAME, this.text_name);

      let lst = this.form_lst.map((x) => x.join("|"));
      let s = lst.join("\n");
      localStorage.setItem(KEY_DATA_FORM, s);

      lst = this.token_lst.map((x) => x.join("|"));
      s = lst.join("\n");
      localStorage.setItem(KEY_DATA_TOKEN, s);

      s = JSON.stringify(this.omogr_json);
      localStorage.setItem(KEY_OMOGR, s);
    } catch (e) {
      alert("Error in LocalStore. => Clean Store\n" + e);
    }
  },
  clear_store: function () {
    localStorage.clear();
    try {
      localStorage.setItem(KEY_TEXT_NAME, this.text_name);
    } catch (e) {
      alert("Error in LocalStore.\n" + e);
    }
  },
  show_store: function () {
    UaLog.log_show("-------------");
    let s = localStorage.getItem(KEY_TEXT_NAME) || "";
    UaLog.log(`${s}`);

    s = localStorage.getItem(KEY_DATA_FORM) || "";
    let size = s.length;
    UaLog.log(`form:${size}`);

    s = localStorage.getItem(KEY_DATA_TOKEN) || "";
    size = s.length;
    UaLog.log(`token:${size}`);

    UaLog.log("-------------");
  },
  save_data: function () {
    const t = get_time();
    this.save_csv(this.form_lst, this.form_file);
    this.save_csv(this.token_lst, this.token_file);
    cmd_log("Save Data   " + t);
    this.set_store();
  },
  save_csv: function (rows, file_name) {
    const rs = rows.map((x) => x.join("|"));
    const data = rs.join("\n");
    const url = `/write${DATA_DIR}/${file_name}`;
    fetch(url, {
      method: "POST",
      cache: "default",
      headers: {
        "Content-Type": "application/json",
      },
      body: data,
    })
      .then((resp) => {
        if (!resp.ok) throw new Error("HTTP error, status=" + resp.status);
        return resp.json();
      })
      .then((json) => {})
      .catch((error) => {
        alert(`ERROR post()\n${url}\n${error}`);
      });
  },
  update_corpus: function (callback) {
    // aggiorna corpus
    // legge corpus_json
    const text_name = `${this.text_name}.form.csv`;
    const url = `/updatecorpus/${text_name}`;
    fetch(url, {
      method: "POST",
      cache: "default",
      headers: {
        "Content-Type": "application/json",
      },
      body: "",
    })
      .then((resp) => {
        if (!resp.ok) {
          throw new Error("HTTP error, status=" + resp.status);
        }
        return resp.json();
      })
      .then((json) => {
        const t = get_time();
        cmd_log("Update Corpus Data   " + t);
        //invoca la funzione per aggiornare  form_lpmx.js
        callback(json);
      })
      .catch((error) => {
        alert(`ERROR post()\n${url}\n${error}`);
      });
  },
  update_text: function () {
    const text_name = `${this.text_name}.form.csv`;
    const url = `/updatetext/${text_name}`;
    fetch(url, {
      method: "POST",
      cache: "default",
      headers: {
        "Content-Type": "application/json",
      },
      body: "",
    })
      .then((resp) => {
        if (!resp.ok) throw new Error("HTTP error, status=" + resp.status);
        return resp.json();
      })
      .then((json) => {
        const t = get_time();
        cmd_log("Update Tex " + this.text_name + "  " + t);
      })
      .catch((error) => {
        alert(`ERROR post()\n${url}\n${error}`);
      });
  },
  load_data: async function () {
    this.clear_store();
    const t = get_time();
    cmd_log("Load Data  " + t);
    if (!this.text_name) return false;
    this.form_lst = await this.load_csv(this.form_file);
    if (this.form_lst.length == 0) return false;
    this.token_lst = await this.load_csv(this.token_file);
    this.omogr_json = await this.load_omogr_json();
    this.sort_form_lst();
    this.set_store();
    return true;
  },
  load_csv: async function (file_name) {
    const url = `${DATA_DIR}/${file_name}`;
    let csv_data = "";
    const resp = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      cache: "no-store",
    });
    if (resp.ok) csv_data = await resp.text();
    if (!csv_data || csv_data.trim().length == 0) {
      const msg = `${file_name} Not Found.`;
      alert(msg);
      //riga vuota per gestione csv
      // da 7 a 8
      csv_data = "|||||||";
    }
    //HACK const rows = ccsv_data.trim().split("\n");
    const rows = clearWnd(csv_data.trim()).split("\n");
    // console.log("load_csv rows",rows.slice(0,10));
    return rows.map((x) => x.split("|"));
  },
  load_omagr: async function () {
    this.omogr_json = await this.load_omogr_json();
    if (this.omogr_json == {}) return false;
    else return true;
  },
  load_omogr_json: async function () {
    const url = URL_CORPUS_OMOGR;
    const resp = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      cache: "no-store",
    });
    if (resp.ok) {
      let text = await resp.text();
      // HACK
      text = clearWnd(text);
      const js = JSON.parse(text);
      return js;
    } else return {};
  },
  load_diff_text_corpus: function (call) {
    const text_name = `${this.text_name}.txt`;
    const url = `/diff?name=${text_name}`;
    fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cace: "no-store",
    })
      .then((resp) => {
        if (!resp.ok) {
          alert("ERROR compare text corpus ");
          return {};
        }
        return resp.json();
      })
      .then((js) => {
        // const s = clearWnd(js);
        call(js);
      })
      .catch((error) => {
        alert(`load_diff_text_corpus() \n${url}\n${error}`);
      });
  },

  //contesto con limite di token a destra e sinistra
  build_context: (cnt_size, i) => {
    let lft = Math.max(i - cnt_size, 0);
    let rgt = Math.min(i + cnt_size + 1, le);
    let row = DbFormLpmx.token_lst.slice(lft, rgt);
    for (let i = 0; i < row.length; i++) row[i].push(lft + i);
    return row;
  },

  build_context_line: (i) => {
    let j = i;
    while (j > -1 && this.token_lst[j][0] !== "##") j--;
    const lft = Math.max(++j, 0);
    let le = this.token_lst.length;
    j = i;
    while (j < le && this.token_lst[j][0] !== "##") j++;
    const rgt = Math.min(j, le);
    let row = this.token_lst.slice(lft, rgt);
    for (let i = 0; i < row.length; i++) row[i].push(lft + i);
    return row;
  },
  // get_formakey_context: function (formakey, cnt_size) {
  //   // filtra utilizzando formakey
  //   alert('B');
  //   let rows = [];
  //   let le = this.token_lst.length;
  //   if (cnt_size > 0) {
  //     for (let i = 0; i < le; i++)
  //       if (this.token_lst[i][1] == formakey)
  //         rows.push(this.build_context(i, cnt_size));
  //     return rows;
  //   }
  //   else {
  //     for (let i = 0; i < le; i++)
  //       if (this.token_lst[i][1] == formakey)
  //         rows.push(this.build_context_line(i));
  //     return rows;
  //   }
  // },

  get_context: function (fr_fk, f_idx, cnt_size) {
    //contesto con limite di token a destra e sinistra
    build_context = (i) => {
      let lft = Math.max(i - cnt_size, 0);
      let rgt = Math.min(i + cnt_size + 1, le);
      let row = this.token_lst.slice(lft, rgt);
      for (let i = 0; i < row.length; i++) row[i].push(lft + i);
      return row;
    };

    // prende  i token da  ## a sinistra a ## a destra
    const build_context_line = (i) => {
      let j = i;
      while (j > -1 && this.token_lst[j][0] !== this.row_eof) j--;
      const lft = Math.max(++j, 0);
      let le = this.token_lst.length;
      j = i;
      while (j < le && this.token_lst[j][0] !== this.row_eof) j++;
      const rgt = Math.min(j, le);
      let row = this.token_lst.slice(lft, rgt);
      for (let i = 0; i < row.length; i++) row[i].push(lft + i);
      return row;
    };

    // f_idx = 1 => formakey
    // f_idx = 0 => forma
    let rows = [];
    let le = this.token_lst.length;
    for (let i = 0; i < le; i++)
      if (this.token_lst[i][f_idx] == fr_fk)
        if (cnt_size > 0) rows.push(build_context(i, cnt_size));
        else rows.push(build_context_line(i));
    return rows;
  },
  get_formakey_context: function (formakey, cnt_size) {
    // filtra utilizzando formakey
    return this.get_context(formakey, 1, cnt_size);
  },
  get_forma_context: function (forma, cnt_size) {
    // filtra utilizzando forma
    return this.get_context(forma, 0, cnt_size);
  },
  sort_form_lst: function () {
    let sortFn = function (a, b) {
      if (a[1] == b[1]) return 0;
      if (a[1] < b[1]) return -1;
      if (a[1] > b[1]) return 1;
    };
    this.form_lst.sort(sortFn);
  },
  fill_rows_text: function () {
    // popola this.rows_js chiamatto da Form_text
    let t_tk_lst = this.token_lst || [];
    this.rows_js = [];
    let len_row_text = 0;
    let row_num = 0;
    let row_t = [];
    let row_tk = [];
    const le = t_tk_lst.length;
    const last = le - 1;

    for (let i = 0; i <= last; i++) {
      const t_tk = t_tk_lst[i];
      const t = t_tk[0];
      const tk = t_tk[1];
      if (t != this.row_eof) {
        row_t.push(t);
        row_tk.push(tk);
        len_row_text += t.length;
      }
      // fine riga
      if (len_row_text > this.len_row || t == this.row_eof || i == last) {
        const row_js = {
          row_n: row_num,
          row_text: row_t.join(" "),
          t: row_t,
          tk: row_tk,
        };
        this.rows_js.push(row_js);
        row_num += 1;
        row_t = [];
        row_tk = [];
        len_row_text = 0;
      }
    }
  },
  filter_rows_js: function (js) {
    // setta this.rows_js
    // i nomi dei campi derivano dall'input di filtraggio
    let formkey = js.formkey.trim();
    let form = js.form.trim();
    let lemma = js.lemma.trim();
    let etimo = js.etimo.trim().toLowerCase();
    let pos = js.pos.trim().toLowerCase();
    let lang = js.lang.trim().toLowerCase(); ///lang
    let rows = this.rows_js;
    let filter_token = () => {
      //setta rows selezionate
      if (form != "")
        rows = rows.filter((x) => {
          return x.t.indexOf(form) > -1;
        });
      if (formkey != "")
        rows = rows.filter((x) => {
          return x.tk.indexOf(formkey) > -1;
        });
    };
    filter_token();
    // struttura dati
    /*
    0: "adonc"
    1: "adonc"
    2: "adonc"
    3: "DUNC"
    4: "it."
    5: "ADJ"
    6: "Pron"
    7: "Masc,Plur,Acc,Pos"
    /*
    0:forma
    1:formakey
    2:lemma
    3:etimo
    4:lang  
    5:pos
    6:funct 
    7:msd (multiplo)
    */
    const iformakei = 1,
      ilemma = 2,
      ietimo = 3,
      ipos = 5,
      ilang = 4;
    let filter_lemma = () => {
      let rs = this.form_lst.slice();
      let le_start = rs.length;
      if (lemma != "")
        rs = rs.filter((x) => {
          return x[ilemma] == lemma;
        });
      if (etimo != "")
        rs = rs.filter((x) => {
          return x[ietimo].toLowerCase() == etimo;
        });
      if (pos != "")
        rs = rs.filter((x) => {
          return x[ipos].toLowerCase() == pos;
        });
      if (lang != "")
        //lang
        rs = rs.filter((x) => {
          return x[ilang] == lang;
        });
      // set dei token corrispondenti al lemma
      let tks = [];
      for (let x of rs) {
        tks.push(x[iformakei]); // tokemkey
      }
      if (rs.length == le_start) tks = [];
      return tks;
    };
    //selezione per lemma
    let tk_set = filter_lemma();
    if (tk_set.length > 0) {
      //x corrisponde a row del text
      rows = rows.filter((x) => {
        let n = 0;
        for (let tk of tk_set) if (x.tk.indexOf(tk) > -1) n += 1;
        return n > 0;
      });
    }
    // rows selezionate
    if (rows.length == 0) {
      this.rows_js = [];
      return;
    }
    //evidenzazione form,formkey e attribuzione numero
    let row_num = 0;
    for (let row of rows) {
      let ws = [];
      for (let i = 0; i < row.t.length; i++) {
        const t = row.t[i];
        const tk = row.tk[i];
        if (tk == formkey) {
          ws.push("<span class='t'>" + t + "</span>");
          continue;
        }
        if (t == form) {
          ws.push("<span class='t'>" + t + "</span>");
          continue;
        }
        if (tk_set.indexOf(tk) > -1) {
          ws.push("<span class='t'>" + t + "</span>");
          continue;
        }
        ws.push(t);
      }
      row.row_text = ws.join(" ");
      row.row_n = row_num;
      row_num++;
    }
    this.rows_js = rows;
  },
  get_row_token_form: function (row_i) {
    //utilizzato da form_text
    const row_js = this.rows_js[row_i];
    const le = row_js.t.length;
    let row_token_form = [];
    for (let i = 0; i < le; i++) {
      const t = row_js.t[i];
      if (UAPUNCTS.indexOf(t) > -1) continue;
      const tk = row_js.tk[i];
      const form_lemma = this.form_lst.find((x) => x[1] == tk);
      if (form_lemma)
        row_token_form.push({
          t: t,
          tk: tk,
          f: form_lemma[0],
          fk: form_lemma[1],
          l: form_lemma[2],
          e: form_lemma[3],
          ph: form_lemma[4],
          pm: form_lemma[5],
          fn: form_lemma[6],
          m: form_lemma[7],
        });
      else
        row_token_form.push({
          t: t,
          tk: tk,
          f: "",
          fk: "",
          l: "",
          e: "",
          ph: "",
          pm: "",
          fn: "",
          m: "",
        });
    }
    return row_token_form;
  },
};
