title: WeasyPrint at PyConFR 2012
published: 2012-09-10
summary: |
    I [gave a talk](http://www.pycon.fr/2012/schedule/presentation/16/)
    about WeasyPrint at PyConFR.


I was at PyConFR in Paris on September 15th and 16th.
I [gave a talk](http://www.pycon.fr/2012/schedule/presentation/16/)
on [WeasyPrint](http://weasyprint.org/) and CSS for print.

**Update 2012-09-12**:
I made [a PDF version](PyConFR_2012_schedule.pdf) of
[the schedule](http://www.pycon.fr/2012/schedule/) for printing, of course
dogfooding WeasyPrint. There is [a bit of CSS](print.css) to remove irrelevant
navigation links, fix some brokenness of the original page, and generally
make it look nice on A4. You can regenerate the same PDF with:

    :::sh
    weasyprint http://www.pycon.fr/2012/schedule/ PyConFR_2012_schedule.pdf \
      -s http://exyr.org/2012/weasyprint-at-pyconfr/print.css

**Update 2012-09-17**:
I think the talk was a success although I forgot a few details. The slides
are below (or [fullscreen](embedder.html#slides.html)), with notes
paraphrasing what I said “on stage”.
The talk and slides were in French (this is PyCon<strong>FR</strong>,
after all) but you, dear international reader, get the English ones.

<iframe
  src="embedder.html#slides.html"
  width="736" height="750" style="border: 2px solid black"></iframe>
