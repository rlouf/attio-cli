use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{DataResponse, ListResponse, Webhook};
use serde::Serialize;

/// List webhooks.
pub async fn list(client: &AttioClient, json: bool) -> Result<()> {
    let response: ListResponse<Webhook> = client.get("/webhooks").await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific webhook.
pub async fn get(client: &AttioClient, webhook_id: &str, json: bool) -> Result<()> {
    let response: DataResponse<Webhook> = client
        .get(&format!("/webhooks/{}", webhook_id))
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new webhook.
pub async fn create(
    client: &AttioClient,
    target_url: &str,
    subscriptions: &str,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        target_url: String,
        subscriptions: Vec<Subscription>,
    }

    #[derive(Serialize)]
    struct Subscription {
        event_type: String,
    }

    // Parse comma-separated subscriptions
    let subs: Vec<Subscription> = subscriptions
        .split(',')
        .map(|s| Subscription {
            event_type: s.trim().to_string(),
        })
        .collect();

    let request = CreateRequest {
        data: CreateData {
            target_url: target_url.to_string(),
            subscriptions: subs,
        },
    };

    let response: DataResponse<Webhook> = client.post("/webhooks", &request).await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update a webhook.
pub async fn update(
    client: &AttioClient,
    webhook_id: &str,
    target_url: Option<&str>,
    subscriptions: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct UpdateRequest {
        data: UpdateData,
    }

    #[derive(Serialize)]
    struct UpdateData {
        #[serde(skip_serializing_if = "Option::is_none")]
        target_url: Option<String>,
        #[serde(skip_serializing_if = "Option::is_none")]
        subscriptions: Option<Vec<Subscription>>,
    }

    #[derive(Serialize)]
    struct Subscription {
        event_type: String,
    }

    let subs = subscriptions.map(|s| {
        s.split(',')
            .map(|e| Subscription {
                event_type: e.trim().to_string(),
            })
            .collect()
    });

    let request = UpdateRequest {
        data: UpdateData {
            target_url: target_url.map(|s| s.to_string()),
            subscriptions: subs,
        },
    };

    let response: DataResponse<Webhook> = client
        .patch(&format!("/webhooks/{}", webhook_id), &request)
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
