# Champipi
Clovis KRZYZANOWSKI and Rudy HEBRARD

# Pour scraper le site (PART 1)
```console
$ python3 main.py part1
```

# Pour préparer le DataFrame et créer les modèles (PART 2 et 3)
```console
$ python3 main.py part2-3
```

# Pour lancer un process et déterminer si un champignon est comestible ou pas
```console
$ python3 main.py process rgb [R] [G] [B] shape [shape VALUES] surface [surface VALUES] model [SVM or TreeClassifier]
```

# Pour lancer le site web
```console
$ cd web/
$ npm install
$ node index.js
```
go to http://localhost:8000/form