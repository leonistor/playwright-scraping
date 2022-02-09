# playwright python learning

## tips:

fish shell "watch": `while true; cat output/contemporanul/contemporanul-articles.jsonl | wc -l; sleep 3; end`


cat without word wrap: `cat output/mytex/articles-mytex.jsonl | cut -c1-180 | less`

### playwright

- block resources https://www.zenrows.com/blog/blocking-resources-in-playwright
- https://www.checklyhq.com/guides/puppeteer-to-playwright/

## toscrape books

- launch global:
    * playwright context
    * jsonl writer jsonlines
    * aiohttp session with custom UA
- use aiohttp to get index pages
- parse index page with SoupStrainer, get links to books pages
- use context to goto each book page
- extract data and write
- pw block images and videos
- aiohttp get article image while


### optional:

- tqdm progress

## bs4

my playground: https://replit.com/@leonistor/SplendidNauticalGame#main.py

- cheatsheet1: http://akul.me/blog/2016/beautifulsoup-cheatsheet/
- cheatsheet2: https://gist.github.com/yoki/b7f2fcef64c893e307c4c59303ead19a

## asyncio scraping

-  https://gist.github.com/madjar/9312452?permalink_comment_id=3494305#gistcomment-3494305
- https://github.com/leimao/Ramachandran/blob/v0.0.2/ramachandran/download.py#L104

## tqdm progress bar with ProcessPool

- https://nedbatchelder.com/blog/202008/do_a_pile_of_work_better.html
- https://gist.github.com/alexeygrigorev/79c97c1e9dd854562df9bbeea76fc5de


## playwright (infinite) scroll page

- https://stackoverflow.com/a/60336607/9727366
- https://github.com/scrapy-plugins/scrapy-playwright#examples
- https://stackoverflow.com/a/69193325/9727366

## http ad blocking proxy

docker run -p 8080:8080 -p 3129:3129 pgnunes/sabproxy
