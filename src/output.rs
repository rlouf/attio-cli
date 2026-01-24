use serde::Serialize;
use std::io::{self, Write};

/// Output format for command results.
#[derive(Debug, Clone, Copy, Default)]
pub enum OutputFormat {
    #[default]
    Table,
    Json,
}

/// Trait for types that can be displayed as a table row.
pub trait TableRow {
    /// Return column headers.
    fn headers() -> Vec<&'static str>;

    /// Return cell values for this row.
    fn row(&self) -> Vec<String>;
}

/// Print a single item.
pub fn print_one<T: Serialize + TableRow>(item: &T, format: OutputFormat) -> io::Result<()> {
    let mut stdout = io::stdout().lock();

    match format {
        OutputFormat::Json => {
            serde_json::to_writer(&mut stdout, item)?;
            writeln!(stdout)?;
        }
        OutputFormat::Table => {
            print_table_single(item, &mut stdout)?;
        }
    }

    Ok(())
}

/// Print multiple items.
pub fn print_many<T: Serialize + TableRow>(items: &[T], format: OutputFormat) -> io::Result<()> {
    let mut stdout = io::stdout().lock();

    match format {
        OutputFormat::Json => {
            // JSONL: one JSON object per line
            for item in items {
                serde_json::to_writer(&mut stdout, item)?;
                writeln!(stdout)?;
            }
        }
        OutputFormat::Table => {
            print_table(items, &mut stdout)?;
        }
    }

    Ok(())
}

/// Print a single item as a table.
fn print_table_single<T: TableRow, W: Write>(item: &T, writer: &mut W) -> io::Result<()> {
    let headers = T::headers();
    let row = item.row();

    // Calculate column widths
    let widths: Vec<usize> = headers
        .iter()
        .zip(row.iter())
        .map(|(h, c)| h.len().max(c.len()))
        .collect();

    // Print header
    for (i, header) in headers.iter().enumerate() {
        if i > 0 {
            write!(writer, "  ")?;
        }
        write!(writer, "{:width$}", header, width = widths[i])?;
    }
    writeln!(writer)?;

    // Print separator
    for (i, width) in widths.iter().enumerate() {
        if i > 0 {
            write!(writer, "  ")?;
        }
        write!(writer, "{}", "-".repeat(*width))?;
    }
    writeln!(writer)?;

    // Print row
    for (i, cell) in row.iter().enumerate() {
        if i > 0 {
            write!(writer, "  ")?;
        }
        let width = widths.get(i).copied().unwrap_or(0);
        write!(writer, "{:width$}", cell, width = width)?;
    }
    writeln!(writer)?;

    Ok(())
}

/// Print items as a table.
fn print_table<T: TableRow, W: Write>(items: &[T], writer: &mut W) -> io::Result<()> {
    if items.is_empty() {
        writeln!(writer, "No results.")?;
        return Ok(());
    }

    let headers = T::headers();
    let rows: Vec<Vec<String>> = items.iter().map(|item| item.row()).collect();

    // Calculate column widths
    let mut widths: Vec<usize> = headers.iter().map(|h| h.len()).collect();
    for row in &rows {
        for (i, cell) in row.iter().enumerate() {
            if i < widths.len() {
                widths[i] = widths[i].max(cell.len());
            }
        }
    }

    // Print header
    for (i, header) in headers.iter().enumerate() {
        if i > 0 {
            write!(writer, "  ")?;
        }
        write!(writer, "{:width$}", header, width = widths[i])?;
    }
    writeln!(writer)?;

    // Print separator
    for (i, width) in widths.iter().enumerate() {
        if i > 0 {
            write!(writer, "  ")?;
        }
        write!(writer, "{}", "-".repeat(*width))?;
    }
    writeln!(writer)?;

    // Print rows
    for row in &rows {
        for (i, cell) in row.iter().enumerate() {
            if i > 0 {
                write!(writer, "  ")?;
            }
            let width = widths.get(i).copied().unwrap_or(0);
            write!(writer, "{:width$}", cell, width = width)?;
        }
        writeln!(writer)?;
    }

    Ok(())
}
