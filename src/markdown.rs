// use pulldown_cmark::CodeBlockKind;
use pulldown_cmark::Event;
use pulldown_cmark::HeadingLevel;
use pulldown_cmark::Tag;
use pulldown_cmark::TagEnd;

pub(crate) fn render(markdown: &str) -> anyhow::Result<String> {
    let options = pulldown_cmark::Options::ENABLE_FOOTNOTES | pulldown_cmark::Options::ENABLE_MATH;
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    // let mut code_lang = None;
    let error = None;
    #[allow(clippy::unnecessary_filter_map)]
    let events = parser.filter_map(|event| match event {
        Event::Start(tag) => {
            match tag {
                // Tag::CodeBlock(CodeBlockKind::Fenced(lang)) => {
                //     if !lang.is_empty() {
                //         code_lang = Some(lang.clone());
                //         // return None;
                //     }
                // }
                Tag::Heading {
                    level,
                    id,
                    classes,
                    attrs,
                } => Some(Event::Start(Tag::Heading {
                    level: downheader(level),
                    id,
                    classes,
                    attrs,
                })),
                tag => Some(Event::Start(tag)),
            }
        }
        Event::End(tag) => {
            match tag {
                // TagEnd::CodeBlock => {
                //     if code_lang.take().is_some() {
                //         // return None;
                //     }
                // }
                TagEnd::Heading(level) => Some(Event::End(TagEnd::Heading(downheader(level)))),
                _ => Some(Event::End(tag)),
            }
        }
        Event::Text(text) => {
            // if let Some(_lang) = &code_lang {
            //     match pygmentize(&text, lang) {
            //         Ok(html) => return Some(Event::Html(html.into())),
            //         Err(err) => error = Some(err),
            //     }
            // }
            Some(Event::Text(text))
        }
        _ => Some(event),
    });

    let mut html = String::new();
    pulldown_cmark::html::push_html(&mut html, events);
    if let Some(err) = error {
        Err(err)
    } else {
        Ok(html.trim().to_owned())
    }
}

fn downheader(level: HeadingLevel) -> HeadingLevel {
    match level {
        HeadingLevel::H1 => HeadingLevel::H3,
        HeadingLevel::H2 => HeadingLevel::H4,
        HeadingLevel::H3 => HeadingLevel::H5,
        HeadingLevel::H4 | HeadingLevel::H5 | HeadingLevel::H6 => HeadingLevel::H6,
    }
}
