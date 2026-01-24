use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Member};

/// List workspace members.
pub async fn list(client: &AttioClient, json: bool) -> Result<()> {
    let response: ListResponse<Member> = client.get("/workspace_members").await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific workspace member.
pub async fn get(client: &AttioClient, member_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Member> = client
        .get(&format!("/workspace_members/{}", member_id))
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
