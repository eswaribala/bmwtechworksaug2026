# 11. CI/CD

# 11. CI/CD

The repository includes GitHub Actions workflows under `.github/workflows`.

## Continuous integration

The `CI` workflow runs on pushes to `main` and on pull requests. It:

- Installs Python dependencies
- Runs Ruff checks
- Runs the pytest suite
- Builds the Sphinx documentation with warnings treated as errors
- Checks Terraform formatting
- Initializes and validates Terraform without using an AWS backend

The existing project contains long lines and deliberate `sys.path` bootstrap
imports in operational scripts, so CI excludes Ruff rules `E501` and `E402`.

## Continuous delivery

The `CD` workflow is manually started from the GitHub Actions tab. It:

1. Authenticates to AWS using GitHub OIDC.
2. Initializes Terraform.
3. Creates a Terraform plan.
4. Applies the plan only when the `apply` input is selected.

The workflow uses the protected GitHub environment `dev`. Configure an
environment secret named `AWS_ROLE_ARN` containing an AWS IAM role trusted by
the GitHub repository. Add required reviewers to the environment before
allowing production deployments.

## GitHub setup

1. Push this repository to GitHub.
2. Create an AWS IAM OIDC provider for
	`https://token.actions.githubusercontent.com`.
3. Create an IAM deployment role restricted to this repository and branch.
4. Add the role ARN as the `AWS_ROLE_ARN` secret in the `dev` environment.
5. Run the CI workflow from a pull request or push.
6. Start the CD workflow manually and select `plan` first.
7. Select `apply` only after reviewing the plan and approving the environment.

AWS access keys must not be committed to the repository or stored as GitHub
secrets when OIDC is available.
