//! Authority Kernel (Rust) — intelligence proposes; authority decides.
//! No model/LLM calls in this crate (GOS-I01 / GOS-I05).

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashSet;

const FORBIDDEN: &[&str] = &["everything", "admin", "Bash(*)", "bash.*"];
const APPROVAL_REQUIRED: &[&str] = &["email.send", "payment.execute", "contract.sign"];

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Decision {
    Allow,
    Deny,
    PendingApproval,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyRequest {
    pub principal: String,
    pub action: String,
    pub capability: String,
    pub resource: String,
    pub granted_capabilities: Vec<String>,
    #[serde(default)]
    pub parent_capabilities: Option<Vec<String>>,
    #[serde(default)]
    pub approval_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthzResult {
    pub decision: Decision,
    pub reason: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub execution_token: Option<String>,
    pub proposal_hash: String,
}

fn content_hash(value: &serde_json::Value) -> String {
    let canonical = serde_json::to_string(value).unwrap_or_default();
    let mut hasher = Sha256::new();
    hasher.update(canonical.as_bytes());
    format!("sha256:{}", hex::encode(hasher.finalize()))
}

fn is_forbidden(cap: &str) -> bool {
    FORBIDDEN.iter().any(|f| *f == cap)
}

/// Deterministic policy evaluation. Never consults a model.
pub fn decide(request: &PolicyRequest, proposal: &serde_json::Value) -> AuthzResult {
    let proposal_hash = content_hash(proposal);
    let granted: HashSet<&str> = request.granted_capabilities.iter().map(|s| s.as_str()).collect();

    if is_forbidden(&request.action) || is_forbidden(&request.capability) {
        return AuthzResult {
            decision: Decision::Deny,
            reason: "forbidden wildcard/admin capability".into(),
            execution_token: None,
            proposal_hash,
        };
    }
    if request.capability != request.action {
        return AuthzResult {
            decision: Decision::Deny,
            reason: "action/capability mismatch".into(),
            execution_token: None,
            proposal_hash,
        };
    }
    if !granted.contains(request.capability.as_str()) {
        return AuthzResult {
            decision: Decision::Deny,
            reason: "capability not granted".into(),
            execution_token: None,
            proposal_hash,
        };
    }
    if let Some(parent) = &request.parent_capabilities {
        let parent_set: HashSet<&str> = parent.iter().map(|s| s.as_str()).collect();
        if !parent_set.contains(request.capability.as_str()) {
            return AuthzResult {
                decision: Decision::Deny,
                reason: "capability not in parent authority (GOS-I04)".into(),
                execution_token: None,
                proposal_hash,
            };
        }
    }
    if APPROVAL_REQUIRED.contains(&request.action.as_str())
        && request.approval_id.as_ref().map(|s| s.is_empty()).unwrap_or(true)
    {
        return AuthzResult {
            decision: Decision::PendingApproval,
            reason: "approval required by policy".into(),
            execution_token: None,
            proposal_hash,
        };
    }

    let token = format!("tok_{}", &proposal_hash[7..23]);
    AuthzResult {
        decision: Decision::Allow,
        reason: "permitted by cedar-aligned policy".into(),
        execution_token: Some(token),
        proposal_hash,
    }
}

/// Child capabilities must be ⊆ parent (GOS-I04).
pub fn validate_child_subset(child: &[String], parent: &[String]) -> Result<(), String> {
    let parent_set: HashSet<&str> = parent.iter().map(|s| s.as_str()).collect();
    let extra: Vec<&str> = child
        .iter()
        .map(|s| s.as_str())
        .filter(|c| !parent_set.contains(c))
        .collect();
    if extra.is_empty() {
        Ok(())
    } else {
        Err(format!("child authority must be ⊆ parent (GOS-I04): extra={extra:?}"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn default_deny_ungranted() {
        let req = PolicyRequest {
            principal: "w1".into(),
            action: "web.read".into(),
            capability: "web.read".into(),
            resource: "https://x".into(),
            granted_capabilities: vec![],
            parent_capabilities: None,
            approval_id: None,
        };
        let r = decide(&req, &json!({"capability": "web.read"}));
        assert_eq!(r.decision, Decision::Deny);
    }

    #[test]
    fn forbid_admin_wildcard() {
        let req = PolicyRequest {
            principal: "w1".into(),
            action: "admin".into(),
            capability: "admin".into(),
            resource: "*".into(),
            granted_capabilities: vec!["admin".into()],
            parent_capabilities: None,
            approval_id: None,
        };
        let r = decide(&req, &json!({}));
        assert_eq!(r.decision, Decision::Deny);
        assert!(r.reason.contains("forbidden"));
    }

    #[test]
    fn child_cannot_expand_parent() {
        let req = PolicyRequest {
            principal: "child".into(),
            action: "email.send".into(),
            capability: "email.send".into(),
            resource: "a@b.c".into(),
            granted_capabilities: vec!["email.send".into()],
            parent_capabilities: Some(vec!["email.draft".into()]),
            approval_id: Some("apr_1".into()),
        };
        let r = decide(&req, &json!({}));
        assert_eq!(r.decision, Decision::Deny);
        assert!(r.reason.contains("GOS-I04"));
    }

    #[test]
    fn allow_when_granted_and_subset() {
        let req = PolicyRequest {
            principal: "w1".into(),
            action: "web.read".into(),
            capability: "web.read".into(),
            resource: "https://x".into(),
            granted_capabilities: vec!["web.read".into(), "filesystem.read".into()],
            parent_capabilities: Some(vec!["web.read".into(), "filesystem.read".into()]),
            approval_id: None,
        };
        let r = decide(&req, &json!({"capability": "web.read"}));
        assert_eq!(r.decision, Decision::Allow);
        assert!(r.execution_token.is_some());
    }

    #[test]
    fn validate_subset_helper() {
        assert!(validate_child_subset(
            &["web.read".into()],
            &["web.read".into(), "email.draft".into()]
        )
        .is_ok());
        assert!(validate_child_subset(&["email.send".into()], &["email.draft".into()]).is_err());
    }
}
