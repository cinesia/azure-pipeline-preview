# Azure Pipeline Preview

## Description
Azure Pipeline Preview (azpp) is a CLI tool designed to preview and validate Azure DevOps pipelines. It allows developers to debug pipeline configurations and ensure correctness before deployment.

## Features
- Preview Azure DevOps pipelines.
- Validate pipeline configurations.
- Debug pipeline issues.
- Manage global and local configurations.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/AzurePipelinePreview.git
   ```
2. Navigate to the project directory:
   ```bash
   cd AzurePipelinePreview
   ```
3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Usage
Run the CLI tool to preview pipelines:
```bash
poetry run python -m azpp.cli preview --help
```

### Example
Preview a pipeline with the following command:
```bash
poetry run python -m azpp.cli preview \
  --organization "my-org" \
  --project "my-project" \
  --pipeline-id 123 \
  --yaml-file "azure-pipelines.yml" \
  --branch-ref "refs/heads/main" \
  --access-token "your-access-token"
```

## Configuration
The tool supports both global and local configurations. Configuration values can be stored in `.azpp` files, either globally (in the user's home directory) or locally (in the current working directory). These files allow you to avoid repeatedly specifying common parameters.

### Global Configuration
Global configuration is stored in the user's home directory and applies to all projects:
```bash
poetry run python -m azpp.cli config \
  --organization "my-org" \
  --project "my-project" \
  --access-token "your-access-token" \
  --global-config
```

### Local Configuration
Local configuration is stored in the current working directory and applies only to the specific project:
```bash
poetry run python -m azpp.cli config \
  --pipeline-id 123 \
  --branch-ref "refs/heads/main" \
  --yaml-file "azure-pipelines.yml"
```

### Configuration Precedence
When running commands, the tool resolves configuration values in the following order:
1. Command-line arguments (highest precedence).
2. Local `.azpp` file.
3. Global `.azpp` file (lowest precedence).

## Contributing
Contributions are welcome! Please follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
Special thanks to all contributors and the open-source community for their support.
