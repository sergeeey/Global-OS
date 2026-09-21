//! gos-authority — process-boundary Authority Kernel CLI.
//! Input JSON on stdin; AuthzResult JSON on stdout. Never calls models.

use authority_kernel::{decide, Decision, PolicyRequest};
use serde::Deserialize;
use serde_json::Value;
use std::io::{self, Read};
use std::process::ExitCode;

#[derive(Debug, Deserialize)]
struct DecideInput {
    request: PolicyRequest,
    #[serde(default)]
    proposal: Value,
}

fn main() -> ExitCode {
    let mut buf = String::new();
    if io::stdin().read_to_string(&mut buf).is_err() {
        eprintln!("failed to read stdin");
        return ExitCode::from(2);
    }
    let input: DecideInput = match serde_json::from_str(&buf) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("invalid input json: {e}");
            return ExitCode::from(2);
        }
    };
    let result = decide(&input.request, &input.proposal);
    match serde_json::to_string(&result) {
        Ok(s) => {
            println!("{s}");
            match result.decision {
                Decision::Allow => ExitCode::SUCCESS,
                Decision::Deny | Decision::PendingApproval => ExitCode::from(1),
            }
        }
        Err(_) => ExitCode::from(2),
    }
}
