# Contributing

## Quick version of setting up your environment

### Python on MacOS

Assuming you use MacOS - otherwise the general commands likely work for all OS's but I won't make an promises

1. Install Homebrew if not installed already:

```shell
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
2. Install pyenv
```shell
brew install pyenv
```
3. Install & activate python 3.9.7 or higher
```shell
pyenv install 3.9.7
pyenv local 3.9.7
```
4. Create and activate venv
```shell
python3 -m venv venv && source venv/bin/activate
```
5. Install requirements
```shell
pip install -r requirements.txt
```
### Manual Testing Requirements

```shell
export GOOGLE_CLOUD_PROJECT=<my-project-id>
# The following account will need cloud monitoring admin role
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
```

### Manual Test Command Example

```shell
python push_deploy_metric.py --team test-team --service test-service --environment test-env --status started --result inactive --version v0.0.0 --metric-value 1
```
