from base64 import b64encode
import json
import requests
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()

APP_NAME = "azpp"

# Define the parameters that can be set globally
GLOBAL_CONFIG_PARAMS = {"organization", "project", "access_token"}
# Define the parameters that can be set locally
LOCAL_CONFIG_PARAMS = {"pipeline_id", "branch_ref", "yaml_file"}
# Define the parameters that can be set globally or locally
ALL_CONFIG_PARAMS = GLOBAL_CONFIG_PARAMS.union(LOCAL_CONFIG_PARAMS)

def load_config_from_file(file_name=".azpp", global_config=False) -> dict:
    """Load configuration from a file."""
    if global_config:
        config_path = Path(typer.get_app_dir(APP_NAME)) / file_name
    else:
        config_path = Path.cwd() / file_name
    config = dict()
    if config_path.exists() and config_path.is_file():
        with config_path.open() as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    if len(config) > 0:
        typer.echo(f"Loaded configuration from {config_path}: {list(config.keys())}")
    else:
        typer.echo(f"No valid configuration found at {config_path}")
    return config

@app.command()
def preview(
    organization: Optional[str] = typer.Option(None, help="Azure DevOps organization"),
    project: Optional[str] = typer.Option(None, help="Azure DevOps project"),
    pipeline_id: Optional[int] = typer.Option(None, help="Azure DevOps pipeline ID"),
    branch_ref: Optional[str] = typer.Option(None, help="Branch reference"),
    yaml_file: Optional[str] = typer.Option(None, help="Path to the YAML file"),
    access_token: Optional[str] = typer.Option(None, help="Personal access token"),
    output_file: str = "preview.yaml",
):
    """
    Run the app, using parameters from the .azpp file or command-line arguments.
    """
    # Load configuration from the .azpp file
    config = load_config_from_file(global_config=True)
    config.update(load_config_from_file(global_config=False))

    # For each parameter, override the value from the .azpp file if provided as a command-line argument
    config['organization'] = organization or config.get('organization')
    config['project'] = project or config.get('project')
    config['pipeline_id'] = pipeline_id or config.get('pipeline_id')
    config['branch_ref'] = branch_ref or config.get('branch_ref')
    config['yaml_file'] = yaml_file or config.get('yaml_file')
    config['access_token'] = access_token or config.get('access_token')

    # Run the app with the provided parameters
    typer.echo(f"Running app with the following parameters:")
    for key, value in config.items():
        typer.echo(f"{key}={value}")

    # Load YAML content
    try:
        with open(config['yaml_file'], "r") as file:
            yaml_content = file.read()
    except FileNotFoundError:
        typer.echo(f"YAML file not found: {config['yaml_file']}")
        raise typer.Exit(code=1)

    # Define the URL for the Pipeline Preview API
    url = f"https://dev.azure.com/{config['organization']}/{config['project']}/_apis/pipelines/{config['pipeline_id']}/preview?api-version=7.1"

    # Create the payload
    payload = {
        "previewRun": True,
        "yamlOverride": yaml_content,
        "resources": {"repositories": {"self": {"refName": config['branch_ref']}}},
        # "templateParameters": {
        #     "simulateCronSchedule": "Monthly Security Scan",
        # }
    }

    # Base64 encode the PAT and set up headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {b64encode(f':{config['access_token']}'.encode()).decode()}",
    }

    # Make the request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        typer.echo(f"HTTP request failed: {e}")
        typer.echo(response.text)
        raise typer.Exit(code=1)

    # Process response
    if response.status_code == 200:
        preview_data = response.json()
        preview_pipeline = preview_data["finalYaml"]
        try:
            with open(output_file, "w", newline="") as file:
                file.write(preview_pipeline)
            typer.echo(
                f"Preview pipeline successful! File has been saved to {output_file}"
            )
        except IOError as e:
            typer.echo(f"Error writing to file {output_file}: {e}")
            raise typer.Exit(code=1)
    else:
        typer.echo(f"Failed to preview pipeline: {response.status_code}")
        typer.echo(response.text)
        raise typer.Exit(code=1)
    
# Set global or local configuration
@app.command()
def config(
    organization: Optional[str] = typer.Option(None, help="Azure DevOps organization"),
    project: Optional[str] = typer.Option(None, help="Azure DevOps project"),
    pipeline_id: Optional[int] = typer.Option(None, help="Azure DevOps pipeline ID"),
    branch_ref: Optional[str] = typer.Option(None, help="Branch reference"),
    yaml_file: Optional[str] = typer.Option(None, help="Path to the YAML file"),
    access_token: Optional[str] = typer.Option(None, help="Personal access token"),
    # Add a global flag to set the configuration globally
    global_config: bool = typer.Option(False, help="Set the configuration globally"),
):
    """
    Set global or local configuration.
    """
    config = load_config_from_file()

    # Update the configuration with the provided values
    config['organization'] = organization or config.get('organization')
    config['project'] = project or config.get('project')
    config['pipeline_id'] = pipeline_id or config.get('pipeline_id')
    config['branch_ref'] = branch_ref or config.get('branch_ref')
    config['yaml_file'] = yaml_file or config.get('yaml_file')
    config['access_token'] = access_token or config.get('access_token')

    # If global_config is set, save the configuration to the global .azpp file
    if global_config:
        config_path = Path.home() / ".azpp"
    else:
        config_path = Path.cwd() / ".azpp"

    with config_path.open("w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    typer.echo(f"Configuration saved to {config_path}")\


if __name__ == "__main__":
    app()
