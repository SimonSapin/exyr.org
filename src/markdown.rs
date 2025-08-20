use pulldown_cmark::CodeBlockKind;
use pulldown_cmark::Event;
use pulldown_cmark::HeadingLevel;
use pulldown_cmark::Tag;

pub(crate) fn render(markdown: &str) -> anyhow::Result<String> {
    let options = pulldown_cmark::Options::ENABLE_FOOTNOTES;
    let parser = pulldown_cmark::Parser::new_ext(markdown, options);
    let mut code_lang = None;
    let error = None;
    #[allow(clippy::unnecessary_filter_map)]
    let events = parser.filter_map(|event| match event {
        Event::Start(tag) => {
            if let Tag::CodeBlock(CodeBlockKind::Fenced(lang)) = &tag {
                if !lang.is_empty() {
                    code_lang = Some(lang.clone());
                    // return None;
                }
            }
            Some(Event::Start(downheader(tag)))
        }
        Event::End(tag) => {
            if let Tag::CodeBlock(_) = &tag {
                if code_lang.take().is_some() {
                    // return None;
                }
            }
            Some(Event::End(downheader(tag)))
        }
        Event::Text(text) => {
            if let Some(_lang) = &code_lang {
                // match pygmentize(&text, lang) {
                //     Ok(html) => return Some(Event::Html(html.into())),
                //     Err(err) => error = Some(err),
                // }
            }
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

fn downheader(tag: Tag) -> Tag {
    if let Tag::Heading(level, id, classes) = tag {
        let level = match level {
            HeadingLevel::H1 => HeadingLevel::H3,
            HeadingLevel::H2 => HeadingLevel::H4,
            HeadingLevel::H3 => HeadingLevel::H5,
            HeadingLevel::H4 | HeadingLevel::H5 | HeadingLevel::H6 => HeadingLevel::H6,
        };
        Tag::Heading(level, id, classes)
    } else {
        tag
    }
}
