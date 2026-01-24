use crate::client::AttioClient;
use crate::error::Result;
use crate::output::{print_many, print_one, OutputFormat};
use crate::types::{Attribute, DataResponse, ListResponse, SelectOption, StatusOption};
use serde::Serialize;

/// List attributes for an object.
pub async fn list(client: &AttioClient, object: &str, json: bool) -> Result<()> {
    let response: ListResponse<Attribute> = client
        .get(&format!("/objects/{}/attributes", object))
        .await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Get a specific attribute.
pub async fn get(client: &AttioClient, object: &str, attribute: &str, json: bool) -> Result<()> {
    let response: DataResponse<Attribute> = client
        .get(&format!("/objects/{}/attributes/{}", object, attribute))
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a new attribute.
pub async fn create(
    client: &AttioClient,
    object: &str,
    title: &str,
    attr_type: &str,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        title: String,
        #[serde(rename = "type")]
        attr_type: String,
    }

    let request = CreateRequest {
        data: CreateData {
            title: title.to_string(),
            attr_type: attr_type.to_string(),
        },
    };

    let response: DataResponse<Attribute> = client
        .post(&format!("/objects/{}/attributes", object), &request)
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update an attribute.
pub async fn update(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    title: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct UpdateRequest {
        data: UpdateData,
    }

    #[derive(Serialize)]
    struct UpdateData {
        #[serde(skip_serializing_if = "Option::is_none")]
        title: Option<String>,
    }

    let request = UpdateRequest {
        data: UpdateData {
            title: title.map(|s| s.to_string()),
        },
    };

    let response: DataResponse<Attribute> = client
        .patch(
            &format!("/objects/{}/attributes/{}", object, attribute),
            &request,
        )
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// List select options for an attribute.
pub async fn list_options(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    json: bool,
) -> Result<()> {
    let response: ListResponse<SelectOption> = client
        .get(&format!(
            "/objects/{}/attributes/{}/options",
            object, attribute
        ))
        .await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a select option.
pub async fn create_option(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    title: &str,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        title: String,
    }

    let request = CreateRequest {
        data: CreateData {
            title: title.to_string(),
        },
    };

    let response: DataResponse<SelectOption> = client
        .post(
            &format!("/objects/{}/attributes/{}/options", object, attribute),
            &request,
        )
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update a select option.
pub async fn update_option(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    option_id: &str,
    title: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct UpdateRequest {
        data: UpdateData,
    }

    #[derive(Serialize)]
    struct UpdateData {
        #[serde(skip_serializing_if = "Option::is_none")]
        title: Option<String>,
    }

    let request = UpdateRequest {
        data: UpdateData {
            title: title.map(|s| s.to_string()),
        },
    };

    let response: DataResponse<SelectOption> = client
        .patch(
            &format!(
                "/objects/{}/attributes/{}/options/{}",
                object, attribute, option_id
            ),
            &request,
        )
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// List status options for an attribute.
pub async fn list_statuses(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    json: bool,
) -> Result<()> {
    let response: ListResponse<StatusOption> = client
        .get(&format!(
            "/objects/{}/attributes/{}/statuses",
            object, attribute
        ))
        .await?;
    print_many(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Create a status option.
pub async fn create_status(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    title: &str,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct CreateRequest {
        data: CreateData,
    }

    #[derive(Serialize)]
    struct CreateData {
        title: String,
    }

    let request = CreateRequest {
        data: CreateData {
            title: title.to_string(),
        },
    };

    let response: DataResponse<StatusOption> = client
        .post(
            &format!("/objects/{}/attributes/{}/statuses", object, attribute),
            &request,
        )
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}

/// Update a status option.
pub async fn update_status(
    client: &AttioClient,
    object: &str,
    attribute: &str,
    status_id: &str,
    title: Option<&str>,
    json: bool,
) -> Result<()> {
    #[derive(Serialize)]
    struct UpdateRequest {
        data: UpdateData,
    }

    #[derive(Serialize)]
    struct UpdateData {
        #[serde(skip_serializing_if = "Option::is_none")]
        title: Option<String>,
    }

    let request = UpdateRequest {
        data: UpdateData {
            title: title.map(|s| s.to_string()),
        },
    };

    let response: DataResponse<StatusOption> = client
        .patch(
            &format!(
                "/objects/{}/attributes/{}/statuses/{}",
                object, attribute, status_id
            ),
            &request,
        )
        .await?;
    print_one(&response.data, OutputFormat::from_json_flag(json))?;
    Ok(())
}
