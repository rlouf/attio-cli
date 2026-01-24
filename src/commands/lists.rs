use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, List, ListResponse};

/// List all lists.
pub async fn list(client: &AttioClient, json: bool) -> Result<()> {
    let response: ListResponse<List> = client.get("/lists").await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific list.
pub async fn get(client: &AttioClient, list: &str, json: bool) -> Result<()> {
    let response: DataResponse<List> = client.get(&format!("/lists/{}", list)).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
