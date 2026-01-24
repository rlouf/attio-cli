use crate::output::TableRow;
use serde::{Deserialize, Serialize};

/// Response from GET /v2/self (identify endpoint).
#[derive(Debug, Serialize, Deserialize)]
pub struct IdentifyResponse {
    pub data: Identity,
}

/// Token identity information.
#[derive(Debug, Serialize, Deserialize)]
pub struct Identity {
    pub workspace: Workspace,
    pub access_type: String,
    #[serde(default)]
    pub scopes: Vec<String>,
}

/// Workspace information.
#[derive(Debug, Serialize, Deserialize)]
pub struct Workspace {
    pub id: WorkspaceId,
    pub name: String,
}

/// Workspace ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct WorkspaceId {
    pub workspace_id: String,
}

impl TableRow for Identity {
    fn headers() -> Vec<&'static str> {
        vec!["WORKSPACE", "WORKSPACE ID", "ACCESS TYPE", "SCOPES"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.workspace.name.clone(),
            self.workspace.id.workspace_id.clone(),
            self.access_type.clone(),
            if self.scopes.is_empty() {
                "-".to_string()
            } else {
                self.scopes.join(", ")
            },
        ]
    }
}

/// Response wrapper for list endpoints.
#[derive(Debug, Serialize, Deserialize)]
pub struct ListResponse<T> {
    pub data: Vec<T>,
}

/// Response wrapper for single item endpoints.
#[derive(Debug, Serialize, Deserialize)]
pub struct DataResponse<T> {
    pub data: T,
}

/// Object definition from the API.
#[derive(Debug, Serialize, Deserialize)]
pub struct Object {
    pub id: ObjectId,
    pub api_slug: String,
    pub singular_noun: String,
    pub plural_noun: String,
}

/// Object ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct ObjectId {
    pub object_id: String,
}

impl TableRow for Object {
    fn headers() -> Vec<&'static str> {
        vec!["SLUG", "SINGULAR", "PLURAL", "ID"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.api_slug.clone(),
            self.singular_noun.clone(),
            self.plural_noun.clone(),
            self.id.object_id.clone(),
        ]
    }
}

/// A record (person, company, or custom object).
#[derive(Debug, Serialize, Deserialize)]
pub struct Record {
    pub id: RecordId,
    #[serde(default)]
    pub values: serde_json::Value,
}

/// Record ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct RecordId {
    pub record_id: String,
    #[serde(default)]
    pub object_id: Option<String>,
}

impl TableRow for Record {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "NAME", "VALUES"]
    }

    fn row(&self) -> Vec<String> {
        // Try to extract a name from common fields
        let name = extract_name(&self.values);

        // Compact representation of values
        let values_str = if self.values.is_null() {
            "-".to_string()
        } else {
            serde_json::to_string(&self.values)
                .unwrap_or_default()
                .chars()
                .take(60)
                .collect::<String>()
                + if serde_json::to_string(&self.values)
                    .unwrap_or_default()
                    .len()
                    > 60
                {
                    "..."
                } else {
                    ""
                }
        };

        vec![self.id.record_id.clone(), name, values_str]
    }
}

/// Try to extract a display name from record values.
pub fn extract_record_name(values: &serde_json::Value) -> String {
    extract_name(values)
}

fn extract_name(values: &serde_json::Value) -> String {
    // Try common name fields
    let candidates = ["name", "full_name", "first_name", "title", "email_addresses"];

    for field in candidates {
        if let Some(value) = values.get(field) {
            if let Some(arr) = value.as_array() {
                // Handle array of values (like email_addresses)
                if let Some(first) = arr.first() {
                    if let Some(s) = first.get("value").and_then(|v| v.as_str()) {
                        return s.to_string();
                    }
                    if let Some(s) = first.get("email_address").and_then(|v| v.as_str()) {
                        return s.to_string();
                    }
                    if let Some(s) = first.as_str() {
                        return s.to_string();
                    }
                }
            }
            if let Some(arr) = value.as_array() {
                if let Some(first) = arr.first() {
                    // Handle name objects with first_name/last_name
                    let first_name = first.get("first_name").and_then(|v| v.as_str());
                    let last_name = first.get("last_name").and_then(|v| v.as_str());
                    if first_name.is_some() || last_name.is_some() {
                        return format!(
                            "{} {}",
                            first_name.unwrap_or(""),
                            last_name.unwrap_or("")
                        )
                        .trim()
                        .to_string();
                    }
                    // Handle full_name
                    if let Some(s) = first.get("full_name").and_then(|v| v.as_str()) {
                        return s.to_string();
                    }
                }
            }
        }
    }

    "-".to_string()
}
