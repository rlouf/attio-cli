use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Task};
use serde::Serialize;

/// List tasks.
pub async fn list(
    client: &AttioClient,
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
    }

    let query = Query { limit, offset };
    let response: ListResponse<Task> = client.post("/tasks/query", &query).await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific task.
pub async fn get(client: &AttioClient, task_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Task> = client.get(&format!("/tasks/{}", task_id)).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new task.
pub async fn create(
    client: &AttioClient,
    content: &str,
    deadline: Option<&str>,
    assignees: Option<&str>,
    linked_records: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        content: String,
        format: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        deadline_at: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        assignees: Option<serde_json::Value>,
        #[serde(skip_serializing_if = "Option::is_none")]
        linked_records: Option<serde_json::Value>,
    }

    let assignees: Option<serde_json::Value> = assignees.map(serde_json::from_str).transpose()?;
    let linked_records: Option<serde_json::Value> =
        linked_records.map(serde_json::from_str).transpose()?;

    let request = CreateRequest {
        data: CreateData {
            content: content.to_string(),
            format: "plaintext".to_string(),
            deadline_at: deadline.map(|s| s.to_string()),
            assignees,
            linked_records,
        },
    };

    let response: DataResponse<Task> = client.post("/tasks", &request).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update a task.
pub async fn update(
    client: &AttioClient,
    task_id: &str,
    content: Option<&str>,
    completed: Option<bool>,
    deadline: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct UpdateRequest {
        data: UpdateData,
    }

    #[derive(Serialize)]
    struct UpdateData {
        #[serde(skip_serializing_if = "Option::is_none")]
        content: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        format: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        is_completed: Option<bool>,
        #[serde(skip_serializing_if = "Option::is_none")]
        deadline_at: Option<String>,
    }

    let request = UpdateRequest {
        data: UpdateData {
            content: content.map(|s| s.to_string()),
            format: content.map(|_| "plaintext".to_string()),
            is_completed: completed,
            deadline_at: deadline.map(|s| s.to_string()),
        },
    };

    let response: DataResponse<Task> = client
        .patch(&format!("/tasks/{}", task_id), &request)
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
