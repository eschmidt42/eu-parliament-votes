# Making sense of EU Parliament Plenary roll call vote PDFs
> Ever wondered if you could visualise the voting behavior of MEPs in the EU Plenary yourself somehow? Wonder no longer! With this repo this is now a thing, well perhaps ... mostly I think ... 


## Why?

After watching Nico Semsrott's video on [Silent Minutes, Missing Votes, Shocking Colleagues](https://www.youtube.com/watch?v=Chg4Vublbgk), where he enthusiastically presented a typical call vote PDF, I got demotivated enough to try and ask my PC for help. 

## State of this

It somehow worked to parse the PDFs, although it was quite a pain. Some very basic insights can probably already be generated across PDF files, although the stability of the parsing was only tested for two PDFs before boredom won out. The parsing with PyPDF2 while convenient seems to have issues with special characters, dropping entire words (like names of MEPs). So some investigation of better practises would be next.

## To dos

* Fix the incorrect parsing of MEP names / them being dropped completely.
* Plot who tends to vote with whom (does Martin Sonneborn still vote randomly?)
* Automate the download of PDFs from the website
