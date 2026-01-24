use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Object};

/// List all objects.
pub async fn list(client: &AttioClient, json: bool) -> Result<()> {
    let response: ListResponse<Object> = client.get("/objects").await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific object.
pub async fn get(client: &AttioClient, object: &str, json: bool) -> Result<()> {
    let response: DataResponse<Object> = client.get(&format!("/objects/{}", object)).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
