title: WeasyPrint at PyConFR 2012
published: 2012-09-10
tags: [kozea, weasyprint]
public: true
summary: |
    I’ll be [giving a talk](http://www.pycon.fr/2012/schedule/presentation/16/)
    about WeasyPrint at PyConFR on Sunday.


I’ll be at PyConFR in Paris this weekend, September 15th and 16th.
I’ll be [giving a talk](http://www.pycon.fr/2012/schedule/presentation/16/)
Sunday 16th at noon, on [WeasyPrint](http://weasyprint.org/) and CSS for print.
The talk will be in French, but the slides in English. I’ll post them here
afterwards.

See you there!

**Update 2012-09-12**:
I made [a PDF version](PyConFR_2012_schedule.pdf) of
[the schedule](http://www.pycon.fr/2012/schedule/) for printing, of course
dogfooding WeasyPrint. There is [a bit of CSS](print.css) to remove irrelevant
navigation links, fix some brokenness of the original page, and generally
make it look nice on A4. You can regenerate the same PDF with:

    :::sh
    weasyprint http://www.pycon.fr/2012/schedule/ PyConFR_2012_schedule.pdf \
      -s http://exyr.org/2012/weasyprint-at-pyconfr/print.css
