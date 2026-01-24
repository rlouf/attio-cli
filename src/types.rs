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

/// Search result from the records search endpoint.
#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: SearchResultId,
    #[serde(default)]
    pub record_text: Option<String>,
    #[serde(default)]
    pub object_slug: Option<String>,
}

/// Search result ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResultId {
    pub record_id: String,
    #[serde(default)]
    pub object_id: Option<String>,
}

impl TableRow for SearchResult {
    fn headers() -> Vec<&'static str> {
        vec!["RECORD ID", "OBJECT", "TEXT"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.id.record_id.clone(),
            self.object_slug.clone().unwrap_or_else(|| "-".to_string()),
            self.record_text.clone().unwrap_or_else(|| "-".to_string()),
        ]
    }
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

/// A list (e.g., Sales Pipeline, Hiring Pipeline).
#[derive(Debug, Serialize, Deserialize)]
pub struct List {
    pub id: ListId,
    pub api_slug: String,
    pub name: String,
    #[serde(default)]
    pub parent_object: Option<Vec<String>>,
    #[serde(default)]
    pub workspace_access: Option<String>,
}

/// List ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct ListId {
    pub list_id: String,
}

impl TableRow for List {
    fn headers() -> Vec<&'static str> {
        vec!["SLUG", "NAME", "PARENT OBJECT", "ID"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.api_slug.clone(),
            self.name.clone(),
            self.parent_object
                .as_ref()
                .map(|v| v.join(", "))
                .unwrap_or_else(|| "-".to_string()),
            self.id.list_id.clone(),
        ]
    }
}

/// An entry in a list.
#[derive(Debug, Serialize, Deserialize)]
pub struct Entry {
    pub id: EntryId,
    #[serde(default)]
    pub parent_record_id: Option<String>,
    #[serde(default)]
    pub values: serde_json::Value,
}

/// Entry ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct EntryId {
    pub entry_id: String,
    #[serde(default)]
    pub list_id: Option<String>,
}

impl TableRow for Entry {
    fn headers() -> Vec<&'static str> {
        vec!["ENTRY ID", "RECORD ID", "VALUES"]
    }

    fn row(&self) -> Vec<String> {
        let record_id = self.parent_record_id.clone().unwrap_or_else(|| "-".to_string());

        let values_str = if self.values.is_null() {
            "-".to_string()
        } else {
            let json = serde_json::to_string(&self.values).unwrap_or_default();
            if json.len() > 60 {
                format!("{}...", &json[..60])
            } else {
                json
            }
        };

        vec![self.id.entry_id.clone(), record_id, values_str]
    }
}

/// A task.
#[derive(Debug, Serialize, Deserialize)]
pub struct Task {
    pub id: TaskId,
    pub content_plaintext: String,
    #[serde(default)]
    pub is_completed: bool,
    #[serde(default)]
    pub deadline_at: Option<String>,
    #[serde(default)]
    pub assignees: Vec<serde_json::Value>,
    #[serde(default)]
    pub linked_records: Vec<serde_json::Value>,
    #[serde(default)]
    pub created_by_actor: Option<serde_json::Value>,
    #[serde(default)]
    pub created_at: Option<String>,
}

/// Task ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskId {
    pub task_id: String,
}

impl TableRow for Task {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "CONTENT", "COMPLETED", "DEADLINE"]
    }

    fn row(&self) -> Vec<String> {
        let content = if self.content_plaintext.len() > 50 {
            format!("{}...", &self.content_plaintext[..50])
        } else {
            self.content_plaintext.clone()
        };

        let completed = if self.is_completed { "✓" } else { "" }.to_string();
        let deadline = self.deadline_at.clone().unwrap_or_else(|| "-".to_string());

        vec![self.id.task_id.clone(), content, completed, deadline]
    }
}

/// A note.
#[derive(Debug, Serialize, Deserialize)]
pub struct Note {
    pub id: NoteId,
    #[serde(default)]
    pub title: Option<String>,
    #[serde(default)]
    pub content_plaintext: Option<String>,
    #[serde(default)]
    pub parent_object: Option<String>,
    #[serde(default)]
    pub parent_record_id: Option<String>,
    #[serde(default)]
    pub created_by_actor: Option<serde_json::Value>,
    #[serde(default)]
    pub created_at: Option<String>,
}

/// Note ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct NoteId {
    pub note_id: String,
}

impl TableRow for Note {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "TITLE", "PARENT", "CREATED"]
    }

    fn row(&self) -> Vec<String> {
        let title = self.title.clone().unwrap_or_else(|| "-".to_string());
        let parent = match (&self.parent_object, &self.parent_record_id) {
            (Some(obj), Some(rec)) => format!("{}:{}", obj, &rec[..8.min(rec.len())]),
            _ => "-".to_string(),
        };
        let created = self
            .created_at
            .as_ref()
            .map(|s| s[..10.min(s.len())].to_string())
            .unwrap_or_else(|| "-".to_string());

        vec![self.id.note_id.clone(), title, parent, created]
    }
}

/// An attribute definition.
#[derive(Debug, Serialize, Deserialize)]
pub struct Attribute {
    pub id: AttributeId,
    pub title: String,
    pub api_slug: String,
    #[serde(rename = "type")]
    pub attr_type: String,
    #[serde(default)]
    pub is_required: bool,
    #[serde(default)]
    pub is_unique: bool,
    #[serde(default)]
    pub is_multiselect: bool,
    #[serde(default)]
    pub is_archived: bool,
}

/// Attribute ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct AttributeId {
    pub attribute_id: String,
    #[serde(default)]
    pub object_id: Option<String>,
}

impl TableRow for Attribute {
    fn headers() -> Vec<&'static str> {
        vec!["SLUG", "TITLE", "TYPE", "REQUIRED", "MULTISELECT"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.api_slug.clone(),
            self.title.clone(),
            self.attr_type.clone(),
            if self.is_required { "✓" } else { "" }.to_string(),
            if self.is_multiselect { "✓" } else { "" }.to_string(),
        ]
    }
}

/// A select option.
#[derive(Debug, Serialize, Deserialize)]
pub struct SelectOption {
    pub id: SelectOptionId,
    pub title: String,
    #[serde(default)]
    pub is_archived: bool,
}

/// Select option ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct SelectOptionId {
    pub option_id: String,
}

impl TableRow for SelectOption {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "TITLE", "ARCHIVED"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.id.option_id.clone(),
            self.title.clone(),
            if self.is_archived { "✓" } else { "" }.to_string(),
        ]
    }
}

/// A status option.
#[derive(Debug, Serialize, Deserialize)]
pub struct StatusOption {
    pub id: StatusOptionId,
    pub title: String,
    #[serde(default)]
    pub is_archived: bool,
    #[serde(default)]
    pub target_time_in_status: Option<i64>,
}

/// Status option ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct StatusOptionId {
    pub status_id: String,
}

impl TableRow for StatusOption {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "TITLE", "ARCHIVED"]
    }

    fn row(&self) -> Vec<String> {
        vec![
            self.id.status_id.clone(),
            self.title.clone(),
            if self.is_archived { "✓" } else { "" }.to_string(),
        ]
    }
}

/// A workspace member.
#[derive(Debug, Serialize, Deserialize)]
pub struct Member {
    pub id: MemberId,
    #[serde(default)]
    pub first_name: Option<String>,
    #[serde(default)]
    pub last_name: Option<String>,
    #[serde(default)]
    pub email_address: Option<String>,
    #[serde(default)]
    pub avatar_url: Option<String>,
    #[serde(default)]
    pub access_level: Option<String>,
}

/// Member ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct MemberId {
    pub workspace_member_id: String,
}

impl TableRow for Member {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "NAME", "EMAIL", "ACCESS"]
    }

    fn row(&self) -> Vec<String> {
        let name = match (&self.first_name, &self.last_name) {
            (Some(f), Some(l)) => format!("{} {}", f, l),
            (Some(f), None) => f.clone(),
            (None, Some(l)) => l.clone(),
            _ => "-".to_string(),
        };

        vec![
            self.id.workspace_member_id.clone(),
            name,
            self.email_address.clone().unwrap_or_else(|| "-".to_string()),
            self.access_level.clone().unwrap_or_else(|| "-".to_string()),
        ]
    }
}

/// A webhook.
#[derive(Debug, Serialize, Deserialize)]
pub struct Webhook {
    pub id: WebhookId,
    pub target_url: String,
    #[serde(default)]
    pub subscriptions: Vec<serde_json::Value>,
    #[serde(default)]
    pub status: Option<String>,
    #[serde(default)]
    pub created_at: Option<String>,
}

/// Webhook ID.
#[derive(Debug, Serialize, Deserialize)]
pub struct WebhookId {
    pub webhook_id: String,
}

impl TableRow for Webhook {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "TARGET URL", "STATUS", "SUBSCRIPTIONS"]
    }

    fn row(&self) -> Vec<String> {
        let subscriptions = if self.subscriptions.is_empty() {
            "-".to_string()
        } else {
            format!("{} events", self.subscriptions.len())
        };

        vec![
            self.id.webhook_id.clone(),
            self.target_url.clone(),
            self.status.clone().unwrap_or_else(|| "-".to_string()),
            subscriptions,
        ]
    }
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
