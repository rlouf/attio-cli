use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Record, SearchResult};
use serde::Serialize;
use std::io::{self, Read};

/// Query parameters for listing records.
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

/// List records of an object type.
pub async fn list(
    client: &AttioClient,
    object: &str,
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

    let response: ListResponse<Record> = client
        .post(&format!("/objects/{}/records/query", object), &query)
        .await?;

    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific record by ID.
pub async fn get(client: &AttioClient, object: &str, record_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Record> = client
        .get(&format!("/objects/{}/records/{}", object, record_id))
        .await?;

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new record.
pub async fn create(
    client: &AttioClient,
    object: &str,
    data: Option<&str>,
    json: bool,
) -> Result<()> {
    let body = get_data_input(data)?;

    #[derive(Serialize)]
    struct CreateRequest {
        data: serde_json::Value,
    }

    let request = CreateRequest {
        data: serde_json::json!({ "values": body }),
    };

    let response: DataResponse<Record> = client
        .post(&format!("/objects/{}/records", object), &request)
        .await?;

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update a record.
pub async fn update(
    client: &AttioClient,
    object: &str,
    record_id: &str,
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
        data: serde_json::json!({ "values": body }),
    };

    let response: DataResponse<Record> = if overwrite {
        // PUT for overwrite
        client
            .put(
                &format!("/objects/{}/records/{}", object, record_id),
                &request,
            )
            .await?
    } else {
        // PATCH for append
        client
            .patch(
                &format!("/objects/{}/records/{}", object, record_id),
                &request,
            )
            .await?
    };

    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Search records.
pub async fn search(
    client: &AttioClient,
    object: &str,
    query: &str,
    limit: Option<u32>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct SearchRequest<'a> {
        query: &'a str,
        objects: Vec<&'a str>,
        #[serde(skip_serializing_if = "Option::is_none")]
        limit: Option<u32>,
    }

    let request = SearchRequest {
        query,
        objects: vec![object],
        limit,
    };

    let response: ListResponse<SearchResult> = client
        .post("/objects/records/search", &request)
        .await?;

    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get data from argument or stdin.
fn get_data_input(data: Option<&str>) -> Result<serde_json::Value> {
    let input = match data {
        Some(d) => d.to_string(),
        None => {
            // Check if stdin has data
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
