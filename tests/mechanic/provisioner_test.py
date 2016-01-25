from unittest import TestCase
import unittest.mock as mock

import rally.config
import rally.mechanic.provisioner
import rally.track.track


class ProvisionerTests(TestCase):
    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.exists')
    @mock.patch('logging.Logger')
    def test_cleanup_nothing(self, mock_logger, mock_path_exists, mock_rm):
        mock_path_exists.return_value = False

        config = rally.config.Config()
        config.add(rally.config.Scope.application, "system", "track.setup.root.dir", "/rally-root/track/track-setup")
        config.add(rally.config.Scope.application, "provisioning", "local.install.dir", "es-bin")
        config.add(rally.config.Scope.application, "provisioning", "install.preserve", False)

        p = rally.mechanic.provisioner.Provisioner(config, mock_logger)
        p.cleanup()

        mock_path_exists.assert_called_once_with('/rally-root/track/track-setup/es-bin')
        mock_rm.assert_not_called()

    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.exists')
    @mock.patch('logging.Logger')
    def test_cleanup_nothing_on_preserve(self, mock_logger, mock_path_exists, mock_rm):
        mock_path_exists.return_value = False

        config = rally.config.Config()
        config.add(rally.config.Scope.application, "system", "track.setup.root.dir", "/rally-root/track/track-setup")
        config.add(rally.config.Scope.application, "provisioning", "local.install.dir", "es-bin")
        config.add(rally.config.Scope.application, "provisioning", "install.preserve", True)
        config.add(rally.config.Scope.application, "provisioning", "datapaths", ["/tmp/some/data-path-dir"])

        p = rally.mechanic.provisioner.Provisioner(config, mock_logger)
        p.cleanup()

        mock_path_exists.assert_not_called()
        mock_rm.assert_not_called()

    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.exists')
    @mock.patch('logging.Logger')
    def test_cleanup(self, mock_logger, mock_path_exists, mock_rm):
        mock_path_exists.return_value = True

        config = rally.config.Config()
        config.add(rally.config.Scope.application, "system", "track.setup.root.dir", "/rally-root/track/track-setup")
        config.add(rally.config.Scope.application, "provisioning", "local.install.dir", "es-bin")
        config.add(rally.config.Scope.application, "provisioning", "install.preserve", False)
        config.add(rally.config.Scope.application, "provisioning", "datapaths", ["/tmp/some/data-path-dir"])

        p = rally.mechanic.provisioner.Provisioner(config, mock_logger)
        p.cleanup()

        expected_dir_calls = [mock.call("/tmp/some/data-path-dir"), mock.call("/rally-root/track/track-setup/es-bin")]
        mock_path_exists.mock_calls = expected_dir_calls
        mock_rm.mock_calls = expected_dir_calls

    @mock.patch('builtins.open')
    @mock.patch('glob.glob', lambda p: ['/install/elasticsearch-3.0.0-SNAPSHOT'])
    @mock.patch('rally.utils.io.unzip')
    @mock.patch('rally.utils.io.ensure_dir')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.exists')
    @mock.patch('logging.Logger')
    def test_prepare(self, mock_logger, mock_path_exists, mock_rm, mock_ensure_dir, mock_unzip, mock_open):
        mock_path_exists.return_value = True

        config = rally.config.Config()
        config.add(rally.config.Scope.application, "system", "env.name", "unittest")
        config.add(rally.config.Scope.application, "system", "track.setup.root.dir", "/rally-root/track/track-setup")
        config.add(rally.config.Scope.application, "builder", "candidate.bin.path", "/data/builds/distributions/")
        config.add(rally.config.Scope.application, "provisioning", "local.install.dir", "es-bin")
        config.add(rally.config.Scope.application, "provisioning", "datapaths", [])

        track_setup = rally.track.track.TrackSetup("test-track", "Description")

        p = rally.mechanic.provisioner.Provisioner(config, mock_logger)
        p.prepare(track_setup)

        self.assertEqual(config.opts("provisioning", "local.binary.path"), "/install/elasticsearch-3.0.0-SNAPSHOT")
