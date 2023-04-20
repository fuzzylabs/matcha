"""Temp doc."""
# def test_is_approved_confirmed():
#     """Test the user can accept a terraform action."""
#     tfs = TerraformService()

#     with mock.patch("typer.confirm") as mock_confirm:
#         mock_confirm.return_value = True
#         assert tfs.is_approved("do")

# def test_is_approved_rejected():
#     """Test the user can reject a terraform action."""
#     tfs = TerraformService()

#     with mock.patch("typer.confirm") as mock_confirm:
#         mock_confirm.return_value = False
#         assert not tfs.is_approved("do")

# def test_provision(terraform_test_config: TerraformConfig):
#     """Test service can provision resources using terraform.

#     Args:
#         terraform_test_config (TerraformConfig): test terraform service config
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config
#     tfs.check_matcha_directory_exists = MagicMock()
#     tfs.check_installation = MagicMock()
#     tfs.validate_config = MagicMock()
#     tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))
#     tfs.terraform_client.apply = MagicMock(return_value=(0, "", ""))
#     tfs.show_terraform_outputs = MagicMock()

#     tfs.is_approved = MagicMock(
#         return_value=False
#     )  # the user does not approve, should not provision
#     with pytest.raises(typer.Exit):
#         tfs.provision()
#         tfs.terraform_client.init.assert_not_called()
#         tfs.terraform_client.apply.assert_not_called()
#         tfs.show_terraform_outputs.assert_not_called()

#     tfs.is_approved = MagicMock(
#         return_value=True
#     )  # the user approves, should provision
#     with does_not_raise():
#         tfs.provision()
#         tfs.terraform_client.init.assert_called()
#         tfs.terraform_client.apply.assert_called()
#         tfs.show_terraform_outputs.assert_called()


# def test_deprovision(terraform_test_config: TerraformConfig):
#     """Test service can destroy resources using terraform.

#     Args:
#         terraform_test_config (TerraformConfig): test terraform service config
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config
#     tfs.check_matcha_directory_exists = MagicMock()
#     tfs.check_installation = MagicMock()
#     tfs.terraform_client.destroy = MagicMock(return_value=(0, "", ""))

#     tfs.is_approved = MagicMock(
#         return_value=False
#     )  # the user does not approve, should not provision
#     with pytest.raises(typer.Exit):
#         tfs.deprovision()
#         tfs.terraform_client.destroy.assert_not_called()

#     tfs.is_approved = MagicMock(
#         return_value=True
#     )  # the user approves, should provision
#     with does_not_raise():
#         tfs.deprovision()
#         tfs.terraform_client.destroy.assert_called()


# def test_write_outputs_state(
#     terraform_test_config: TerraformConfig,
#     mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
#     expected_outputs: dict,
# ):
#     """Test service writes the state file correctly.

#     Args:
#         terraform_test_config (TerraformConfig): test terraform service config
#         mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
#         expected_outputs (dict): expected output from terraform
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config

#     tfs.terraform_client.output = MagicMock(wraps=mock_output)

#     with does_not_raise():
#         tfs.write_outputs_state()
#         with open(terraform_test_config.state_file) as f:
#             assert json.load(f) == expected_outputs


# def test_show_terraform_outputs(
#     terraform_test_config: TerraformConfig,
#     capsys: SysCapture,
#     mock_output: Callable[[str, bool], Union[str, Dict[str, str]]],
#     expected_outputs: dict,
# ):
#     """Test service shows the correct terraform output.

#     Args:
#         terraform_test_config (TerraformConfig): test terraform service config
#         capsys (SysCapture): fixture to capture stdout and stderr
#         mock_output (Callable[[str, bool], Union[str, Dict[str, str]]]): the mock output
#         expected_outputs (dict): expected output from terraform
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config

#     tfs.terraform_client.output = MagicMock(wraps=mock_output)
#     with does_not_raise():
#         tfs.show_terraform_outputs()
#         captured = capsys.readouterr()

#         for output in expected_outputs:
#             assert output in captured.out


# def test_terraform_raise_exception_provision_init(
#     terraform_test_config: TerraformConfig,
# ):
#     """Test if terraform exception is handled correctly during init when provisioning resources.

#     Args:
#         terraform_test_config (TerraformConfig): terraform test service config
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config
#     tfs.check_matcha_directory_exists = MagicMock()
#     tfs.check_installation = MagicMock()
#     tfs.validate_config = MagicMock()
#     tfs.terraform_client.init = MagicMock(return_value=(1, "", "Init failed"))

#     tfs.is_approved = MagicMock(
#         return_value=True
#     )  # the user approves, should provision

#     with pytest.raises(MatchaTerraformError) as exc_info:
#         tfs.provision()
#     assert (
#         str(exc_info.value)
#         == "Terraform failed because of the following error: 'Init failed'."
#     )


# def test_terraform_raise_exception_provision_apply(
#     terraform_test_config: TerraformConfig,
# ):
#     """Test if terraform exception is handled correctly during apply when provisioning resources.

#     Args:
#         terraform_test_config (TerraformConfig): terraform test service config
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config
#     tfs.check_matcha_directory_exists = MagicMock()
#     tfs.check_installation = MagicMock()
#     tfs.validate_config = MagicMock()
#     tfs.terraform_client.init = MagicMock(return_value=(0, "", ""))
#     tfs.terraform_client.apply = MagicMock(return_value=(1, "", "Apply failed"))
#     tfs.show_terraform_outputs = MagicMock()

#     tfs.is_approved = MagicMock(
#         return_value=True
#     )  # the user approves, should provision

#     with pytest.raises(MatchaTerraformError) as exc_info:
#         tfs.provision()
#         tfs.terraform_client.init.assert_called()
#     assert (
#         str(exc_info.value)
#         == "Terraform failed because of the following error: 'Apply failed'."
#     )


# def test_terraform_raise_exception_deprovision_destroy(
#     terraform_test_config: TerraformConfig,
# ):
#     """Test if terraform exception is captured when performing deprovision.

#     Args:
#         terraform_test_config (TerraformConfig): terraform test service config
#     """
#     tfs = TerraformService()
#     tfs.config = terraform_test_config

#     tfs.check_matcha_directory_exists = MagicMock()
#     tfs.check_installation = MagicMock()
#     tfs.terraform_client.destroy = MagicMock(return_value=(1, "", "Destroy failed"))

#     tfs.is_approved = MagicMock(
#         return_value=True
#     )  # the user approves, should deprovision

#     with pytest.raises(MatchaTerraformError) as exc_info:
#         tfs.deprovision()
#     assert (
#         str(exc_info.value)
#         == "Terraform failed because of the following error: 'Destroy failed'."
#     )
