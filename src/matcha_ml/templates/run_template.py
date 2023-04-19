"""Run terraform templates to provision and deprovision resources."""
import dataclasses
import os


@dataclasses.dataclass
class TerraformConfig:
    """Configuration required for terraform."""

    # Path to terraform template are stored
    working_dir: str = os.path.join(os.getcwd(), ".matcha", "infrastructure")

    # state file to store output after terraform apply
    state_file: str = os.path.join(working_dir, "matcha.state")

    # variables file
    var_file: str = os.path.join(working_dir, "terraform.tfvars.json")

    # if set to False terraform output will be printed to stdout/stderr
    # else no output will be printed and (ret_code, out, err) tuple will be returned
    capture_output: bool = True
