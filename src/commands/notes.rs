use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Note};
use serde::Serialize;

/// List notes.
pub async fn list(
    client: &AttioClient,
    parent_object: Option<&str>,
    parent_record_id: Option<&str>,
    limit: Option<u32>,
    offset: Option<u32>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct Query {
        #[serde(skip_serializing_if = "Option::is_none")]
        limit: Option<u32>,
        #[serde(skip_serializing_if = "Option::is_none")]
        offset: Option<u32>,
        #[serde(skip_serializing_if = "Option::is_none")]
        parent_object: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        parent_record_id: Option<String>,
    }

    let query = Query {
        limit,
        offset,
        parent_object: parent_object.map(|s| s.to_string()),
        parent_record_id: parent_record_id.map(|s| s.to_string()),
    };

    let response: ListResponse<Note> = client.post("/notes/query", &query).await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific note.
pub async fn get(client: &AttioClient, note_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Note> = client.get(&format!("/notes/{}", note_id)).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new note.
pub async fn create(
    client: &AttioClient,
    title: &str,
    parent_object: &str,
    parent_record_id: &str,
    content: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        parent_object: String,
        parent_record_id: String,
        title: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        content: Option<String>,
        format: String,
    }

    let request = CreateRequest {
        data: CreateData {
            parent_object: parent_object.to_string(),
            parent_record_id: parent_record_id.to_string(),
            title: title.to_string(),
            content: content.map(|s| s.to_string()),
            format: "plaintext".to_string(),
        },
    };

    let response: DataResponse<Note> = client.post("/notes", &request).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
