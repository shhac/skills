# Infrastructure as Code Focus Pack

Load when changed files include Terraform (`.tf`, `.tfvars`, modules), CloudFormation/CDK, Helm charts, Kubernetes manifests, Dockerfiles, or environment-tier configuration such as scaling/capacity values, instance sizes, or IAM and network policy.

Look for:

- Blast radius: which environments and resources does this plan actually touch? Prod values changed alongside dev (scaling floors, instance classes, retention), shared modules whose change fans out to every consumer.
- Destruction and replacement of stateful resources: changes that force replacement of databases, volumes, queues, or clusters; missing `prevent_destroy`/deletion-protection on stateful resources; state moves/renames that a plan will read as destroy-and-create.
- Security widening: security-group or firewall rules opening `0.0.0.0/0`, IAM policies gaining `*` actions or resources, buckets or endpoints becoming public, encryption or logging quietly disabled.
- Rollout ordering with application code: infra that must exist before code that uses it deploys (queues, topics, tables, secrets), or removal of infra that running code still references.
- Cost cliffs: instance-class jumps, provisioned-capacity increases, retention or replication changes with a standing cost, resources created per-environment or per-tenant that multiply.
- Drift between mirrored environments: a change applied to one env whose siblings are expected to match, without the matching change or a stated reason.
- Secrets or credentials in plaintext tfvars, manifests, or Docker build args.
- Scheduled/temporary capacity changes (prescales, load tests) without the matching unwind or an explicit note of when and how they revert.

Good findings name the affected environment and resource, state whether the risk is at plan time or apply time, and suggest the smallest safer direction: split prod from dev changes, add deletion protection, narrow the policy, sequence the dependent PRs, or document the unwind.

Reference basis: Terraform/IaC production practice and cloud provider well-architected guidance.
