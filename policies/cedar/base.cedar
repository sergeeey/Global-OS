# policies/cedar/base.cedar
# Default-deny authorization surface for Global OS Authority Kernel.
# Cedar is the policy language; runtime may evaluate via cedar engine or
# equivalent deterministic PolicyEngine (see kernel/policy).

permit (
  principal,
  action == Action::"web.read",
  resource
)
when {
  context has capability &&
  context.capability == "web.read"
};

permit (
  principal,
  action == Action::"filesystem.read",
  resource
)
when {
  context has capability &&
  context.capability == "filesystem.read"
};

permit (
  principal,
  action == Action::"email.draft",
  resource
)
when {
  context has capability &&
  context.capability == "email.draft"
};

# email.send requires explicit approval context
permit (
  principal,
  action == Action::"email.send",
  resource
)
when {
  context has capability &&
  context.capability == "email.send" &&
  context has approval_id &&
  context.approval_id != ""
};

# Forbidden wildcards — documented non-permits:
# NO Action::"Bash(*)"
# NO Action::"everything"
# NO Action::"admin"
