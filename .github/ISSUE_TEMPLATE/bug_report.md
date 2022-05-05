---
name: Bug Report
about: Create a report to help us improve
title: ''
labels: 'bug'
assignees: ''

---

**Describe the bug**
<!--- A clear and concise description of what the bug is. -->


**To Reproduce**
<!--
Steps to reproduce the issue:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error
-->

**Expected behavior**
<!--- A clear and concise description of what you expected to happen. -->

**Screenshots/Logs**
<!--- 
If applicable, add screenshots, logs or error outputs to help explain your problem.

To give us more information for diagnosing the issue, make sure to enable debug logging for both bentoctl and BentoML:

Enable via environment variable, e.g.:
```
$ git clone git@github.com:bentoml/BentoML.git && cd bentoml
$ BENTOCTL_DEBUG=True BENTOML_DEBUG=TRUE python guides/quick-start/main.py
```

Or set debug logging in your Python code:
```python
from bentoml.configuration import set_debug_mode
set_debug_mode(True)
```

For bentoctl CLI commands, simply add the `--verbose` flag, e.g.:
```bash
bentoctl init --verbose
```

-->


**Environment:**
 - OS: [e.g. MacOS 10.14.3]
 - Python Version [e.g. Python 3.7.1]
 - BentoML Version [e.g. BentoML-0.8.6]
 - Bentoctl Version [e.g. bentoctl-0.1]


**Additional context**
<!-- Add any other context about the problem here. e.g. links to related discussion. -->
