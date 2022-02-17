# ziare RO

## BZB

arhiva: https://bzb.ro/arhiva/2020#archive

- 2021: `for i in (seq 7364 7607); python bzb.py --edition $i; end`
- 2020: `for i in (seq 7119 7363); python bzb.py --edition $i; end`
- 2019: `for i in (seq 6876 7118); python bzb.py --edition $i; end`
- 2018: `for i in (seq 6633 6875); python bzb.py --edition $i; end`
- 2017: `for i in (seq 6393 6632); python bzb.py --edition $i; end`
- 2016: `for i in (seq 6144 6392); python bzb.py --edition $i; end`
- 2015: `for i in (seq 5887 6143); python bzb.py --edition $i; end`
- 2014: `for i in (seq 5592 5886); python bzb.py --edition $i; end`
- 2013: `for i in (seq 5293 5591); python bzb.py --edition $i; end`
- 2012: `for i in (seq 4995 5292); python bzb.py --edition $i; end`
- 2011: `for i in (seq 4694 4994); python bzb.py --edition $i; end`
- 2010: `for i in (seq 4388 4693); python bzb.py --edition $i; end`
- 2009: `for i in (seq 4085 4387); python bzb.py --edition $i; end`
- 2008: `for i in (seq 3780 4084); python bzb.py --edition $i; end`
- 2007: `for i in (seq 3480 3779); python bzb.py --edition $i; end`
- 2006: `for i in (seq 3177 3479); python bzb.py --edition $i; end`

## Contemporanul

doar din 2014

arhiva: https://www.contemporanul.ro/arhiva

## mytex

navigation sucks. must use playwright

unique urls:

```bash
cat input/articles-mytex.txt | sort | uniq -u | wc -l
```

## TODO

- https://www.catavencii.ro/
- https://www.biziday.ro/
- https://www.veridica.ro/ro
- cu abonament pt arhiva: https://newsweek.ro/
