# Published benchmark snapshots

This directory keeps the latest safe, tracked snapshot for each model. It contains submitted source, installable theme and Playground packages, screenshots, public checks and concise telemetry when an execution generated an artifact.

- [GPT-6 Astra](gpt-6-astra/latest/)
- [Claude Fable 5.1](claude-fable-5-1/latest/)

Raw output remains under the ignored repository-root `results/` directory. It is not committed because manifests and request checkpoints may contain hidden reference material. Use `python3 -m benchmark.publish_results` after a reviewed round to replace one model's `latest` snapshot.
