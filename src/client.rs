use crate::error::{ApiError, Result};
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE};
use reqwest::{Client, Method, Response, StatusCode};
use serde::de::DeserializeOwned;
use serde::Serialize;

const BASE_URL: &str = "https://api.attio.com/v2";

/// Client for the Attio API.
#[derive(Debug, Clone)]
pub struct AttioClient {
    http: Client,
    api_key: String,
}

impl AttioClient {
    /// Create a new client with the given API key.
    pub fn new(api_key: String) -> Result<Self> {
        let http = Client::builder()
            .user_agent(concat!("attio-cli/", env!("CARGO_PKG_VERSION")))
            .build()?;

        Ok(Self { http, api_key })
    }

    /// Make a GET request.
    pub async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T> {
        self.request(Method::GET, path, Option::<()>::None).await
    }

    /// Make a POST request with a JSON body.
    pub async fn post<T: DeserializeOwned, B: Serialize>(&self, path: &str, body: &B) -> Result<T> {
        self.request(Method::POST, path, Some(body)).await
    }

    /// Make a PUT request with a JSON body.
    pub async fn put<T: DeserializeOwned, B: Serialize>(&self, path: &str, body: &B) -> Result<T> {
        self.request(Method::PUT, path, Some(body)).await
    }

    /// Make a PATCH request with a JSON body.
    pub async fn patch<T: DeserializeOwned, B: Serialize>(
        &self,
        path: &str,
        body: &B,
    ) -> Result<T> {
        self.request(Method::PATCH, path, Some(body)).await
    }

    /// Make a DELETE request.
    pub async fn delete(&self, path: &str) -> Result<()> {
        let response = self.send(Method::DELETE, path, Option::<()>::None).await?;
        self.handle_error(response).await?;
        Ok(())
    }

    /// Internal: make a request and parse the JSON response.
    async fn request<T: DeserializeOwned, B: Serialize>(
        &self,
        method: Method,
        path: &str,
        body: Option<B>,
    ) -> Result<T> {
        let response = self.send(method, path, body).await?;
        let response = self.handle_error(response).await?;
        let data = response.json().await?;
        Ok(data)
    }

    /// Internal: send a request and return the raw response.
    async fn send<B: Serialize>(
        &self,
        method: Method,
        path: &str,
        body: Option<B>,
    ) -> Result<Response> {
        let url = format!("{}{}", BASE_URL, path);

        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", self.api_key))
                .expect("Invalid API key format"),
        );
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

        let mut request = self.http.request(method, &url).headers(headers);

        if let Some(body) = body {
            request = request.json(&body);
        }

        let response = request.send().await?;
        Ok(response)
    }

    /// Handle API error responses.
    async fn handle_error(&self, response: Response) -> Result<Response> {
        let status = response.status();

        if status.is_success() {
            return Ok(response);
        }

        // Try to parse error body for details
        let error_body: Option<serde_json::Value> = response.json().await.ok();
        let message = error_body
            .as_ref()
            .and_then(|v| v.get("message"))
            .and_then(|m| m.as_str())
            .unwrap_or("Unknown error")
            .to_string();

        let api_error = match status {
            StatusCode::UNAUTHORIZED => ApiError::Unauthorized,
            StatusCode::FORBIDDEN => ApiError::Forbidden {
                scope: extract_scope(&message).unwrap_or_default(),
            },
            StatusCode::NOT_FOUND => ApiError::NotFound {
                resource: "resource".to_string(),
                id: "unknown".to_string(),
            },
            StatusCode::UNPROCESSABLE_ENTITY | StatusCode::BAD_REQUEST => {
                ApiError::Validation { message }
            }
            StatusCode::TOO_MANY_REQUESTS => ApiError::RateLimited {
                retry_after_secs: 60, // Default, could parse from header
            },
            _ => ApiError::Server {
                status: status.as_u16(),
                message,
            },
        };

        Err(api_error.into())
    }
}

/// Try to extract a scope name from an error message.
fn extract_scope(message: &str) -> Option<String> {
    // Simple heuristic: look for words ending in :read or :write
    message
        .split_whitespace()
        .find(|word| word.contains(":read") || word.contains(":write"))
        .map(|s| s.trim_matches(|c: char| !c.is_alphanumeric() && c != ':' && c != '_'))
        .map(String::from)
}
