# 人工痴脳のチノちゃん

自然言語解析の一手法としてマルコフ連鎖を用いて、文章の自動生成を行い人工無能を作成した。

![tino](https://user-images.githubusercontent.com/28590220/28707050-c6847c8e-73b1-11e7-9e62-dc055ec797a6.png)


## 1. 実行手順

```rb
git clone https://github.com/END98/nobrain-chino
cd nobrain-chino
python http-server.py
```

でローカルサーバを立てて、nobrain-chino/app/simple.htmlをクリックすれば動作する。

```rb
http://localhost:8000/app/simple.html
```

でチノちゃんの実力を見てみよう。チノちゃんをクリックすると声だしたり動いたりもするよ。


<br>


### システム構成図
追加予定


## 2. 主要な技術: マルコフ連鎖
マルコフ連鎖とは、確率過程の一種であり、状態が離散(有限もしくは可算)なものを指す。
今回はマルコフ連鎖を用いて文章をつなぎ合わせる手法で文章を作る解説をする。

### 定義
マルコフ連鎖は、一連の確率変数　X1, X2, X3, ... で現在の状態が決まっていれば、過去及び未来の状態は独立であるものである。形式的には、


$$ Pr(X_n+1 = x | X_n = x_n, ... , X_1 = x_1, X_0 = x_0) = Pr(X_n+1 = x | X_n + x_n) $$

Xiの取りうる値は、連鎖の状態空間と呼ばれ、可算集合Sをなす。
マルコフ連鎖は有向グフラで表現され、エッジはある状態から他の状態へ変異する確率を表示する

例: 有限状態機械
時刻nに置いて状態yにあるとすると、それが時刻n+1に置いて状態xに動く確率が、現在の状態に依存し、時刻nに依存しない

### 理解
地点A,B,Cから別の各地点へ移動する確率(矢印上の数値)が存在する。
X回数試行した(X回移動させた)場合の到着地点の確率を求めたい。

マルコフ連鎖は、移動回数Xを増やすと、最初の地点(A,B,C)に関係なく、X回移動した後の到着地点の確率がある値に収束することを発見した。

<img width="319" alt="markov" src="https://user-images.githubusercontent.com/28590220/28662922-c50bc97c-72f6-11e7-8392-62951d526ee5.png">

[参考文献](http://www.housecat442.com/?p=83)


<br>

## 3. 実装


### ライブラリ
janome : Python自身で記述された形態素解析エンジン。Pythonのみで書かれているためMeCabなどの外部ライブラリを導入する必要性がない。形態素解析に使用する辞書一式もMeCabを使っているため精度に違いはないが、解析にかかる時間は10倍ほど遅い。


```rb
$ pip install janome
```

janome.py

```rb
from janome.tokenizeer import Tokenizer

t = Tokenizer()
malist = t.tokenize("庭には二羽鶏がいる")
for n in malist:
    print(n)
```

実行結果

```
$ python3 tu-janome.py

庭      名詞,一般,*,*,*,*,庭,ニワ,ニワ
に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
二      名詞,数,*,*,*,*,二,ニ,ニ
羽      名詞,接尾,助数詞,*,*,*,羽,ワ,ワ
鶏      名詞,一般,*,*,*,*,鶏,ニワトリ,ニワトリ
が      助詞,格助詞,一般,*,*,*,が,ガ,ガ
いる    動詞,自立,*,*,一段,基本形,いる,イル,イル
。      記号,句点,*,*,*,*,。,。,。

```

tokenizerオブジェクトを生成し、tokenize()メソッドに形態素解析を行いたい文章を指定する。

<br>

### 手法
(1)文章を単語に分解(形態素解析)する
(2)単語の前後の結びつきを辞書に登録する
(3)辞書を利用して作文する

辞書の生成方法は、分かち書きした文章を、前後の結びつきで登録する。
「彼は猫が好きだ」という言葉があるのであれば、「彼｜は｜猫｜が｜好き｜だ」と文章を分割する。これらの前後三単語に注目し、以下のように辞書へ登録する。

彼｜は｜猫
は｜猫｜が
猫｜が｜好き
が｜好き｜だ

以下の猫に関することわざを辞書として与えたとするとき、この辞書を基にして同じ組み合わせを持つ単語と単語をランダムに組み合わせて文章を生成する。

猫｜に｜小判｜。
魚｜を｜猫｜に｜預ける｜。
窮鼠｜猫｜を｜嚙む｜。
預ける｜猫｜も｜鰹節。

例えば、文頭の『猫』を使うとした場合、猫に繋がる要素は『猫｜に』と『猫｜を』と『猫｜も』となる。『に』を選択した場合、次に繋がる要素は『に｜小判』、『に｜預ける』となる。『預ける』を採用した場合、次は『。』もしくは、『鰹節』となる。『鰹節』を選択した場合、次の要素は『。』だけなので文末だと判断できる。結果、オリジナルな文章として『猫に預ける鰹節。』という文章を生成する。


### コード

markov.py

```rb
from janome.tokenizer import Tokenizer
import os, re, json, random

dict_file = "chatbot-data.json"
dic = {}
tokenizer = Tokenizer() # janome

# 辞書に単語を記録する
def register_dic(words):
    global dic
    if len(words) == 0: return
    tmp = ["@"]
    for i in words:
        word = i.surface
        if word == "" or word == "\r\n" or word == "\n": continue
        tmp.append(word)
        if len(tmp) < 3: continue
        if len(tmp) > 3: tmp = tmp[1:]
        set_word3(dic, tmp)
        if word == "。" or word == "？":
            tmp = ["@"]
            continue
    # 辞書を更新するごとにファイルへ保存
    json.dump(dic, open(dict_file,"w", encoding="utf-8"))

# 三要素のリストを辞書として登録
def set_word3(dic, s3):
    w1, w2, w3 = s3
    if not w1 in dic: dic[w1] = {}
    if not w2 in dic[w1]: dic[w1][w2] = {}
    if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0
    dic[w1][w2][w3] += 1

# 作文する
def make_sentence(head):
    if not head in dic: return ""
    ret = []
    if head != "@": ret.append(head)        
    top = dic[head]
    w1 = word_choice(top)
    w2 = word_choice(top[w1])
    ret.append(w1)
    ret.append(w2)
    while True:
        if w1 in dic and w2 in dic[w1]:
            w3 = word_choice(dic[w1][w2])
        else:
            w3 = ""
        ret.append(w3)
        if w3 == "。" or w3 == "？" or w3 == "": break
        w1, w2 = w2, w3
    return "".join(ret)

def word_choice(sel):
    keys = sel.keys()
    return random.choice(list(keys))

# チャットボットに返答させる
def make_reply(text):
    # まず単語を学習する
    if text[-1] != "。": text += "。"
    words = tokenizer.tokenize(text)
    register_dic(words)
    # 辞書に単語があれば、そこから話す
    for w in words:
        face = w.surface
        ps = w.part_of_speech.split(',')[0]
        if ps == "感動詞":
            return face + "。"
        if ps == "名詞" or ps == "形容詞":
            if face in dic: return make_sentence(face)
    return make_sentence("@")

# 辞書があれば最初に読み込む
if os.path.exists(dict_file):
    dic = json.load(open(dict_file,"r"))
```






















