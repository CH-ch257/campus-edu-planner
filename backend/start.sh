#!/bin/bash
cd /d/zuoye/campus-edu-planner/backend
source venv/Scripts/activate
export HF_ENDPOINT=https://hf-mirror.com
uvicorn main:app --reload
