Wstęp
---
Celem ćwiczenia jest zbadanie zachowania sortowania przy wykorzystaniu
równoległej wersji sortowania kubełkowego zaimplementowanej przy wykorzystaniu
biblioteki OpenMP.

Eksperyment
---

Ekperyment polega na posortowaniu tablicy losowo wygenerowanych liczb, przy
wykorzystaniu zrównoleglonej metody sortowaniua kubełkowego. Sortowanie
zostało zrównoleglone na dwa sposoby.

### Metoda 1

Pierwszy ze sposobów zakładał istnienie globalnych kubełków, do których
dostęp będzie synchronizowany.

![Diagram metody pierwszej](imgs/tpr_lab3_method1.png)


#### Określenie rozmiaru kubełków

Pierwszym krokiem było obliczenie ilości elementów w każdym z kubełków.
Każdy z wątków otrzymał zakres tablicy do przeszukania. Efektem tego działania
była tablica `occurences[bucket_no] = items in bucket`. Zapis do tej
tablicy odbywał się z każdego z wątków, zatem stanowiła ona sekcję
krytyczną. Później, na podstawie tej tablicy, obliczono kolejną tablicę
`starts`, które wskazywała początkowy indeks dla każdego z kubełków.
Dzięki temu jednoznaczenie można było określić gdzie w tablicy jest początek
oraz koniec każdego z kubełków.


#### Podział tablicy na kubełki

Kolejnym krokiem było przepisanie elementów z początkowej tablicy, do tablicy
docelowej. Jest to tożsame z podziałem na kubełki.
Możliwe to było dzięki wykorzystaniu tablicy `starts`.
Każdemu z kubełków został przypisany jeden wątek. Każdy z wątków przeszukuje
całą tablicę.
Gdy wątek trafi na element, który powinien trafić do "jego" kubełka przepisuje
go do docelowej tablicy z indeksem `starts[bucket_no]` oraz inkrementuje
wartość.
Takie podejście pozwala uniknąć potrzeby synchronizacji, ponieważ
każdy wartość jest modyfikowana jedynie przez jeden wątek.

Implementacja tej metody znajduje się w pliku `bucket.c`.

#### Sortowanie kubełków

Ostatnim krokiem jest posortowanie wartości w każdym z kubełków. Wykorzystana
do tego została funkcja `void qsort(void * tab, size_t num, size_t size, ( * comparator ) ( const void *, const void * ) );`
dostarczona przez bibliotekę standardową.


#### Pomiar czasu

Do pomiaru czasu wykorzystano funkcję z biblioteki OpenMP `double omp_get_wtime()`.
Pomiar rozpoczynał się po wypełnieniu tablicy, natomiast kończył gdy
każdy z kubełków został posortowany.

### Metoda 2

Metryki
---

### Przyśpieszenie (speedup)
Jest miarą, która mówi o ile obliczenie będzie wykonane szybciej, gdy dołożymy kolejny
procesor. Definiuje się jako iloraz czasu wykonania na jedny procesorze
oraz czasu wykonania na `n` procesorach.

### Wydajność (efficiency)
Jest miarą, która mówi w jakim stopniu została wykorzystana moc obliczeniowa,
gdy zostały dołożone kolejne procesory. Określić jaka część czasu została
wykorzystana na faktyczne obliczenia, a jaka została zmarnowana na
komunikację i synchronizację.
Definiuje się ją jako iloraz przyśpieszenia i liczby procesorów.

### Miara Karpa-Flatta
Pozwala określić jaka część algorytmu jest sekwencyjna.


Infrastruktura
---
Eksperyment został zrealizowany na klastrze obliczeniowym ZEUS.

Wykorzystano
 - jeden węzeł obliczeniowy
 - 12 procesorów węzła

Procesor na którym przeprowadzane były obliczenia:
```
    Intel(R) Xeon(R) CPU X5650 6C 2.66GHz
```

Wyniki
---

Wnioski i podsumowanie
---
