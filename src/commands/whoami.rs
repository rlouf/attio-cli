use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_one, OutputFormat};
use crate::types::IdentifyResponse;

/// Execute the whoami command.
pub async fn execute(client: &AttioClient, json: bool) -> Result<()> {
    let response: IdentifyResponse = client.get("/self").await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
