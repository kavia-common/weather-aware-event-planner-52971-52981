#!/bin/bash
cd /home/kavia/workspace/code-generation/weather-aware-event-planner-52971-52981/event_planner_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

