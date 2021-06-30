# Copyright 2016-2020 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
#
# This file is intended to be run with Python 3.6 or above, so it should only
# use features available in that version.

import argparse
from collections import namedtuple
from contextlib import closing
from datetime import timedelta
import http
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
from tempfile import mkdtemp
import time

try:
    from maas_api_helper import (
        capture_script_output,
        Config,
        get_base_url,
        geturl,
        MD_VERSION,
        signal,
    )
except ImportError:
    # for tests
    from snippets.maas_api_helper import (
        capture_script_output,
        Config,
        get_base_url,
        geturl,
        MD_VERSION,
        signal,
    )

import yaml


class ScriptsDir:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = Path(mkdtemp())
        self.scripts = base_path / "scripts"
        self.out = base_path / "out"
        self.downloads = base_path / "downloads"

    def ensure(self):
        for directory in (self.scripts, self.out, self.downloads):
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir()


ScriptRunResult = namedtuple(
    "ScriptRunResult",
    ["exit_status", "status", "error", "runtime", "result_files"],
)


class Script:
    def __init__(self, info, maas_url, dirs):
        self.info = info
        self.maas_url = maas_url
        self.dirs = dirs

    @property
    def command(self):
        return [self.dirs.scripts / self.info["path"]]

    @property
    def name(self):
        return self.info["name"]

    @property
    def combined_path(self):
        return self.dirs.out / self.name

    @property
    def stdout_path(self):
        return self.dirs.out / "{name}.out".format(name=self.name)

    @property
    def stderr_path(self):
        return self.dirs.out / "{name}.err".format(name=self.name)

    @property
    def result_path(self):
        return self.dirs.out / "{name}.yaml".format(name=self.name)

    @property
    def environ(self):
        env = os.environ.copy()
        env.update(
            {
                "MAAS_BASE_URL": self.maas_url,
                "OUTPUT_COMBINED_PATH": self.combined_path,
                "OUTPUT_STDOUT_PATH": self.stdout_path,
                "OUTPUT_STDERR_PATH": self.stderr_path,
                "RESULT_PATH": self.result_path,
                "DOWNLOAD_PATH": self.dirs.downloads,
                "HAS_STARTED": str(self.info.get("has_started", False)),
                "RUNTIME": str(self.info.get("timeout_seconds")),
            }
        )
        if "bmc_config_path" in self.info:
            env["BMC_CONFIG_PATH"] = self.info["bmc_config_path"]
        return env

    def should_run(self):
        """Whether the script should be run."""
        return self.info.get(
            "default", False
        ) and "deploy-info" in self.info.get("tags", [])

    def run(self):
        exit_status = 0
        start = time.monotonic()
        proc = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.environ,
        )
        try:
            capture_script_output(
                proc,
                self.combined_path,
                self.stdout_path,
                self.stderr_path,
                timeout_seconds=self.info.get("timeout_seconds"),
            )
        except OSError as e:
            if e.errno != 0:
                exit_status = e.errno
        except subprocess.TimeoutExpired:
            exit_status = 124
        runtime = time.monotonic() - start

        return ScriptRunResult(
            exit_status,
            *self._get_status_and_error(exit_status),
            runtime,
            self._get_result_files(),
        )

    def _get_status_and_error(self, exit_status):
        status = "WORKING"
        error = None
        if exit_status == 124:
            status = "TIMEDOUT"
            error = "Timeout({timeout}) expired on {script}".format(
                timeout=timedelta(seconds=self.info.get("timeout_seconds")),
                script=self.name,
            )
        elif exit_status != 0:
            status = "FAILED"
            error = "Failed to execute {script}: {exit_status}".format(
                script=self.name,
                exit_status=exit_status,
            )
        return status, error

    def _get_result_files(self):
        return {
            path.name: path.read_bytes()
            for path in (
                self.stdout_path,
                self.stderr_path,
                self.combined_path,
                self.result_path,
            )
            if path.exists()
        }


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="run MAAS commissioning scripts and report back results"
    )
    parser.add_argument(
        "--config",
        help="cloud-init config with MAAS credentials and endpoint, (e.g. /etc/cloud/cloud.cfg.d/90_dpkg_local_cloud_config.cfg)",
        type=argparse.FileType(),
    )
    parser.add_argument(
        "--metadata-url",
        help="MAAS metadata URL",
    )
    parser.add_argument(
        "--token-key",
        "--tk",
        help="OAuth token key",
    )
    parser.add_argument(
        "--token-secret",
        "--ts",
        help="OAuth token secret",
    )
    parser.add_argument(
        "--consumer-key",
        "--ck",
        help="OAuth consumer key",
    )
    parser.add_argument(
        "--consumer-secret",
        "--cs",
        help="OAuth consumer secret",
    )
    ns = parser.parse_args(args=args)
    return ns


def get_config(ns):
    if ns.config:
        with closing(ns.config) as fd:
            conf = yaml.safe_load(fd)["reporting"]["maas"]
    else:
        conf = {}

    data = {}
    for key in (
        "token_key",
        "token_secret",
        "consumer_key",
        "consumer_secret",
    ):
        ns_value = getattr(ns, key)
        data[key] = ns_value if ns_value is not None else conf.get(key)

    url = conf.get("endpoint")
    ns_url = getattr(ns, "metadata_url")
    if ns_url is not None:
        url = ns_url
    data["metadata_url"] = url

    config = Config()
    config.update(data)
    return config


def fetch_scripts(maas_url, metadata_url, dirs, credentials):
    res = geturl(metadata_url + "maas-scripts", credentials=credentials)
    if res.status == http.client.NO_CONTENT:
        sys.exit(1)

    with tarfile.open(mode="r|*", fileobj=BytesIO(res.read())) as tar:
        tar.extractall(dirs.scripts)

    with (dirs.scripts / "index.json").open() as fd:
        data = json.load(fd)

    return [
        Script(script_info, maas_url, dirs)
        for script_info in data["1.0"]["commissioning_scripts"]
    ]


def main(args):
    config = get_config(parse_args(args))

    dirs = ScriptsDir()
    dirs.ensure()

    maas_url = get_base_url(config.metadata_url)
    metadata_url = maas_url + "/MAAS/metadata/" + MD_VERSION + "/"

    for script in fetch_scripts(
        maas_url, metadata_url, dirs, config.credentials
    ):
        if not script.should_run():
            continue
        result = script.run()
        signal(
            metadata_url,
            config.credentials,
            result.status,
            error=result.error,
            script_name=script.name,
            script_result_id=script.info.get("script_result_id"),
            files=result.result_files,
            runtime=result.runtime,
            exit_status=result.exit_status,
            script_version_id=script.info.get("script_version_id"),
        )


if __name__ == "__main__":
    main(sys.argv[1:])
