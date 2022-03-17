# Web Analysis
```mermaid
classDiagram
Crawler <|-- GoalCrawler
Crawler <|-- SkySportCrawler
Crawler <|-- CNNCrawler
Crawler <|-- BBCCrawler
Crawler <|-- SiamSportCrawler
CrawlerManager -->Crawler
Scrap <|-- GoalScrap
Scrap <|-- SkySportScrap
Scrap <|-- CNNScrap
Scrap <|-- BBCScrap
ScrapManager-->Scrap
```