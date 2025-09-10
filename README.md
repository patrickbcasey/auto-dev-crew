## How to setup the project:

pip install -r requirements.txt

<!-- Requirements generated with uv pip freeze > requirements.txt -->

## Create a .env file and insert your model information:

#### using ollama:

```Dotenv
MODEL_BASE_URL=http://localhost:11434
API_BASE=http://localhost:11434
MODEL_NAME=INSERT_YOUR_MODEL_NAME_HERE
```

#### using OpenAI:

```Dotenv
OPENAI_API_KEY=INSERT_YOUR_OPENAI_API_KEY_HERE
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=INSERT_YOUR_OPENAI_MODEL_NAME_HERE
```

### To run the program:

panel serve app/src/autodevcrew_flow/main.py

### To run in benchmark mode:

Place your SWE-bench.json file containing the SWE-bench task information and tasks.txt containing the list of instance_ids to run file in the [bench_files](./bench_files/) folder.  
Sample versions of these files can be found in [the samples folder](./sample/)
