use anyhow::ensure;
use std::process::{Command, ExitCode};

mod build;
mod markdown;

const RSYNC_DESTINATION: &str = "alwaysdata:exyr.org/";

fn try_main() -> anyhow::Result<()> {
    match std::env::args().nth(1).as_deref() {
        Some("build") => build::build(),
        Some("watch") => watch(),
        Some("serve") => serve(),
        Some("diff") => diff(),
        Some("meld") => meld(),
        Some("up") => up(),
        _ => {
            anyhow::bail!("Usage: cargo run [build | watch | serve | diff | meld | up] ")
        }
    }
}

fn build_dir() -> std::path::PathBuf {
    build::project_dir().join("build")
}

fn watch() -> anyhow::Result<()> {
    let status = Command::new("cargo")
        .args(["watch", "-x", "run build"])
        .spawn()?
        .wait()?;
    ensure!(status.success(), "cargo watch error");
    Ok(())
}

fn serve() -> anyhow::Result<()> {
    build::build()?;
    let status = Command::new("python3")
        .args(["-m", "http.server", "-b", "127.0.0.1", "-d"])
        .arg(build_dir())
        .spawn()?
        .wait()?;
    ensure!(status.success(), "Python server error");
    Ok(())
}

fn diff() -> anyhow::Result<()> {
    build::build()?;
    let status = Command::new("delta")
        .arg("/home/simon/backup/alwaysdata/exyr/exyr.org/")
        .arg(build_dir())
        .spawn()?
        .wait()?;
    ensure!(status.success(), "Diff error");
    Ok(())
}

fn meld() -> anyhow::Result<()> {
    build::build()?;
    let _child = Command::new("meld")
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .arg("/home/simon/backup/alwaysdata/exyr/exyr.org/")
        .arg(build_dir())
        .spawn()?;
    // Not waiting
    Ok(())
}

fn up() -> anyhow::Result<()> {
    build::build()?;
    let status = Command::new("rsync")
        .args(["-ah", "--del", "--info=progress2,stats"])
        // Include a trailing slash to tell rsync to copy the contents of the build dir,
        // not the directory named `build` itself.
        .arg(build_dir().join(""))
        .arg(RSYNC_DESTINATION)
        .spawn()?
        .wait()?;
    ensure!(status.success(), "rsync error");
    Ok(())
}

fn main() -> ExitCode {
    match try_main() {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            eprintln!("{err}");
            ExitCode::FAILURE
        }
    }
}
