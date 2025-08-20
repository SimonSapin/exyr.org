use crate::markdown;
use regex_lite::Regex;
use std::fs;
use std::io;
use std::path::PathBuf;

pub(crate) fn project_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

#[derive(serde::Deserialize)]
#[serde(deny_unknown_fields)]
struct FrontMatter {
    title: String,
    summary: String,
    published: String,
    #[serde(default)]
    modified: String,
}

#[derive(serde::Serialize)]
struct Page {
    url: String,
    slug: String,
    title: String,
    published: String,
    updated: String,
    summary_html: String,
    html: String,
}

pub(crate) fn build() -> anyhow::Result<()> {
    let start = std::time::Instant::now();

    let project_dir = project_dir();
    let pages_dir = project_dir.join("pages");
    let static_dir = project_dir.join("static");
    let build_dir = project_dir.join("build");
    let build_static_dir = build_dir.join("static");

    not_found_as_none(fs::remove_dir_all(&build_dir))?;
    fs::create_dir_all(&build_dir)?;
    fs::create_dir_all(&build_static_dir)?;

    fs::copy(static_dir.join("htaccess"), build_dir.join(".htaccess"))?;
    fs::copy(static_dir.join("gone.html"), build_dir.join("gone.html"))?;
    fs::copy(
        static_dir.join("favicon.png"),
        build_static_dir.join("favicon.png"),
    )?;
    fs::copy(
        static_dir.join("feed-icon.png"),
        build_static_dir.join("feed-icon.png"),
    )?;

    let template_env = template_env();
    let pygments_css = fs::read_to_string(static_dir.join("pygments.css"))?;
    let ctx = minijinja::context! { pygments_css => pygments_css };
    let css = template_env.get_template("style.css")?.render(ctx)?;
    fs::write(build_dir.join("style.css"), minify_css(css)?)?;

    let page_template = template_env.get_template("flatpage.html")?;
    let mut posts_by_year = Vec::new();
    for result in fs::read_dir(&pages_dir)? {
        let entry = result?;
        let file_name = entry.file_name();
        let year = file_name.to_str().unwrap();
        if !year.chars().all(|c| c.is_ascii_digit()) {
            continue;
        }

        let build_year_dir = build_dir.join(year);
        fs::create_dir_all(&build_year_dir)?;

        let mut pages = Vec::new();
        let year_dir = entry.path();
        for result in fs::read_dir(&year_dir)? {
            let entry = result?;
            if entry.metadata()?.is_dir() {
                copy_dir(&entry.path(), &build_year_dir.join(entry.file_name()))?;
                continue;
            }
            let file_name = entry.file_name();
            let file_name = file_name.to_str().unwrap();
            let Some(slug) = file_name.strip_suffix(".md") else {
                continue;
            };

            println!("Reading pages/{year}/{file_name}");
            let contents = fs::read_to_string(entry.path())?;

            let (meta, body) = contents
                .split_once("\n\n")
                .ok_or(anyhow::anyhow!("Missing metadata marker"))?;

            let html_path = year_dir.join(format!("{slug}.html"));
            let html = if let Some(html) = not_found_as_none(fs::read_to_string(html_path))? {
                html.trim().to_owned()
            } else {
                markdown::render(body)?
            };

            let meta: FrontMatter = serde_yaml::from_str(meta)?;
            let page = Page {
                url: format!("https://exyr.org/{year}/{slug}/"),
                slug: slug.to_owned(),
                title: meta.title,
                updated: if meta.modified.is_empty() {
                    meta.published.clone()
                } else {
                    meta.modified
                },
                published: meta.published,
                summary_html: markdown::render(&meta.summary)?,
                html,
            };

            let ctx = minijinja::context! { page => &page };
            let rendered = page_template.render(ctx)?;
            let page_dir = build_year_dir.join(slug);
            fs::create_dir_all(&page_dir)?;
            fs::write(page_dir.join("index.html"), rendered)?;

            pages.push(page);
        }
        if !pages.is_empty() {
            pages.sort_by_key(|page| page.published.clone());
            pages.reverse();
            posts_by_year.push((year.parse::<u32>().unwrap(), pages));
        }
    }

    posts_by_year.sort_by_key(|&(year, _)| year);
    posts_by_year.reverse();
    let latest_year = posts_by_year[0].0;
    let ctx = minijinja::context! {
        about => markdown::render(&fs::read_to_string(pages_dir.join("about.md"))?)?,
        posts_by_year => &posts_by_year,
    };
    let rendered = template_env.get_template("all_posts.html")?.render(ctx)?;
    fs::write(build_dir.join("index.html"), rendered)?;

    let mut articles = posts_by_year
        .into_iter()
        .flat_map(|(_year, posts)| posts)
        .collect::<Vec<_>>();
    articles.sort_by_key(|page| page.updated.clone());
    articles.reverse();
    let ctx = minijinja::context! {
        articles => articles,
        latest_year => latest_year,
        feed_updated => &articles[0].updated,
    };
    let rendered = template_env.get_template("atom.xml")?.render(ctx)?;
    fs::write(build_dir.join("feed.atom"), rendered)?;

    // TODO:
    // * static in page

    println!("Built in {:.03} s", start.elapsed().as_secs_f32());
    Ok(())
}

fn not_found_as_none<T>(result: io::Result<T>) -> io::Result<Option<T>> {
    match result {
        Ok(x) => Ok(Some(x)),
        Err(err) if err.kind() == io::ErrorKind::NotFound => Ok(None),
        Err(err) => Err(err),
    }
}

fn template_env() -> minijinja::Environment<'static> {
    let mut env = minijinja::Environment::new();
    let templates_dir = project_dir().join("templates");
    env.set_loader(minijinja::path_loader(templates_dir));
    env.set_undefined_behavior(minijinja::UndefinedBehavior::Strict);

    // https://github.com/pallets/markupsafe/blob/4afaf1ae7a/src/markupsafe/__init__.py#L21
    let strip_comments_re = Regex::new("(?s)<!--.*?-->").unwrap();
    let strip_tags_re = Regex::new("(?s)<.*?>").unwrap();
    // https://github.com/pallets/markupsafe/blob/4afaf1ae7a/src/markupsafe/__init__.py#L140
    env.add_filter("striptags", move |value: String| {
        let value = strip_comments_re.replace_all(&value, "");
        let value = strip_tags_re.replace_all(&value, "");
        value.split_whitespace().collect::<Vec<_>>().join(" ")
    });

    env
}

fn minify_css(mut css: String) -> anyhow::Result<String> {
    for (re, replacement) in [
        // Remove comments. *? is the non-greedy version of *
        (r#"/\*.*?\*/"#, ""),
        // Remove redundant whitespace
        (r#"\s+"#, " "),
        // Put back line breaks after block so that it's not just one huge line
        (r#"} ?"#, "}\n"),
    ] {
        css = Regex::new(re)?.replace_all(&css, replacement).into_owned();
    }

    let header = "\
        /*\n\
        Non-minified version is at\n\
        https://github.com/SimonSapin/exyr.org/blob/master/exyr/templates/style.css\n\
        */\n\
    ";
    Ok(format!("{header}{css}"))
}

fn copy_dir(source_dir: &PathBuf, dest_dir: &PathBuf) -> anyhow::Result<()> {
    fs::create_dir_all(dest_dir)?;
    for result in fs::read_dir(source_dir)? {
        let entry = result?;
        let dest = dest_dir.join(entry.file_name());
        let meta = entry.metadata()?;
        if meta.is_dir() {
            copy_dir(&entry.path(), &dest)?;
        } else {
            anyhow::ensure!(
                meta.is_file(),
                "{} is neither a directory nor file",
                entry.path().display()
            );
            fs::copy(entry.path(), dest)?;
        }
    }
    Ok(())
}
