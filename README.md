# Making sense of EU Parliament Plenary roll call vote PDFs
> Ever wondered if you could visualise the voting behavior of MEPs in the EU Plenary yourself somehow? Wonder no longer! With this repo this is now a thing, well perhaps ... mostly I think ... 


```
from eu_parliament import download
```

## Context

Currently this repo is using PyPDF2 to parse PDFs behind _[Result of roll call votes available](https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes)_. And the notebook already contains a dazzling Plotly visulisation!

**Why?**

After watching Nico Semsrott's video on [Silent Minutes, Missing Votes, Shocking Colleagues](https://www.youtube.com/watch?v=Chg4Vublbgk), where he enthusiastically presented a typical call vote PDF, I got demotivated enough to try and ask my PC for help. 

**State of this**

It somehow worked to parse the PDFs, although it was quite a pain. Some very basic insights can probably already be generated across PDF files, although the stability of the parsing was only tested for two PDFs before boredom won out. The parsing with PyPDF2 while convenient seems to have issues with special characters, dropping entire words (like names of MEPs). So some investigation of better practises would be next.

**To dos**

* Fix the incorrect parsing of MEP names / them being dropped completely.
* Plot who tends to vote with whom (does Martin Sonneborn still vote randomly?)
* Automate the download of PDFs from the website

## How to use

### Downloading

Collecting the links

```
%%time
rcv_pdfs, vot_pdfs = download.identify_links_for_pdfs(download.URL)
```

Downloading the roll call pdfs

```
%%time
download.collect_multiple_files(rcv_pdfs)
```

Downloading the other pdfs

```
%%time
download.collect_multiple_files(vot_pdfs)
```

### Parsing

### Visualising
