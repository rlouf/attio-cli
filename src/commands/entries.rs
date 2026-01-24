use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, Entry, ListResponse};
use serde::Serialize;
use std::io::{self, Read};

/// Query parameters for listing entries.
#[derive(Debug, Serialize)]
struct ListQuery {
    #[serde(skip_serializing_if = "Option::is_none")]
    limit: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    offset: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    filter: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sorts: Option<serde_json::Value>,
}

/// List entries in a list.
pub async fn list(
    client: &AttioClient,
    list: &str,
    limit: Option<u32>,
    offset: Option<u32>,
    filter: Option<&str>,
    sort: Option<&str>,
    json: bool,
) -> Result<()> {
    let filter = filter.map(serde_json::from_str).transpose()?;
    let sorts = sort.map(serde_json::from_str).transpose()?;

    let query = ListQuery {
        limit,
        offset,
        filter,
        sorts,
    };

    let response: ListResponse<Entry> = client
        .post(&format!("/lists/{}/entries/query", list), &query)
        .await?;

    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific entry by ID.
pub async fn get(client: &AttioClient, list: &str, entry_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Entry> = client
        .get(&format!("/lists/{}/entries/{}", list, entry_id))
        .await?;

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new entry.
pub async fn create(
    client: &AttioClient,
    list: &str,
    record_id: &str,
    data: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        parent_record_id: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        entry_values: Option<serde_json::Value>,
    }

    let entry_values = if let Some(d) = data {
        Some(serde_json::from_str(d)?)
    } else if !atty::is(atty::Stream::Stdin) {
        let mut buf = String::new();
        io::stdin().read_to_string(&mut buf)?;
        if buf.trim().is_empty() {
            None
        } else {
            Some(serde_json::from_str(&buf)?)
        }
    } else {
        None
    };

    let request = CreateRequest {
        data: CreateData {
            parent_record_id: record_id.to_string(),
            entry_values,
        },
    };

    let response: DataResponse<Entry> = client
        .post(&format!("/lists/{}/entries", list), &request)
        .await?;

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update an entry.
pub async fn update(
    client: &AttioClient,
    list: &str,
    entry_id: &str,
    data: Option<&str>,
    overwrite: bool,
    json: bool,
) -> Result<()> {
    let body = get_data_input(data)?;

    #[derive(Serialize)]
    struct UpdateRequest {
        data: serde_json::Value,
    }

    let request = UpdateRequest {
        data: serde_json::json!({ "entry_values": body }),
    };

    let response: DataResponse<Entry> = if overwrite {
        client
            .put(
                &format!("/lists/{}/entries/{}", list, entry_id),
                &request,
            )
            .await?
    } else {
        client
            .patch(
                &format!("/lists/{}/entries/{}", list, entry_id),
                &request,
            )
            .await?
    };

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get data from argument or stdin.
fn get_data_input(data: Option<&str>) -> Result<serde_json::Value> {
    let input = match data {
        Some(d) => d.to_string(),
        None => {
            if atty::is(atty::Stream::Stdin) {
                return Err(crate::error::Error::Input(
                    "Missing JSON data. Provide as argument or pipe via stdin.".to_string(),
                ));
            }

            let mut buf = String::new();
            io::stdin().read_to_string(&mut buf)?;
            buf
        }
    };

    serde_json::from_str(&input).map_err(Into::into)
}
