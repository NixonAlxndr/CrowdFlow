# Branching [!!!IMPORTANT!!!]
Github ini terdapat 3 branch, yaitu main, yolo, dan yolo-2, dimana setiap branch itu adalah hasil tesging untuk mencari model terbaik yang telah kami buat. Setelah melakukan beberapa tunning pada model dan revisi, maka model dengan nama yolo11s.pt adalah model yang terbaik, dan model ini terdapat pada brancing 'yolo-2' jadi untuk menjalankan web kami, silahkan menggunakan 
git pull ke branch **yolo-2**, atau menggunakan command:

```
  git clone -b yolo-2 https://github.com/NixonAlxndr/CrowdFlow.git
```

# Installation
FE (Front End)
Untuk bagian Front End, kami menggunakan npm untuk runtime nya sehingga, untuk menjalankan web kami, maka diperlukan runtime npm.
Setelah repository ini berhasil di clone, maka kita harus masuke ke folder Front-End terlebih dahulu, dan menjalankan
```
npm install
```
dimana command ini diperlukan untuk menginstall semua dependency di package.json.
Setelah menginstall semua dependency, kita bisa menjalankan command
```
npm run dev
```
Dimana command ini diperlukan untuk menjalankan web di browser

BE (Back End)
Untuk bagian Back End, kami menggunakan bahasa python, dimana semua dependency sudah berada di file requirements.txt, sehingga untuk menginstall semua requirement itu kita perlu masuk ke folder Back-End, dan menjalankan command:
```
pip install -r requirements.txt
```
Setelah menjalankan command itu maka, kita bisa menjalankan API Back End kita dengan command:
```
uvicorn main:app --reload
```
