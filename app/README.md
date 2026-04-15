# Resume Agent Demo App

A small Python web app with a public HTML frontend and two agent tools:

- Read resume content from a local file or an S3 path
- Run demo CLI commands

## Quick start

1. Create a virtual environment
2. Install dependencies from requirements.txt
3. Copy .env.example to .env and add your OpenAI key
4. Run the app with python main.py
5. Open http://localhost:8080

## Docker run script

You can build and run the container directly with the included shell script.

By default, the script will source:

- .env.local

You can also point it to a different file:

ENV_FILE=/path/to/your.env ./run_docker.sh

Example:

HOST_PORT=8080 ./run_docker.sh

Optional environment variables supported by the script include:

- OPENAI_API_KEY
- OPENAI_MODEL
- FLASK_SECRET_KEY
- AWS_REGION
- AWS_DEFAULT_REGION
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_SESSION_TOKEN
- S3_BUCKET_NAME
- IMAGE_NAME
- CONTAINER_NAME
- HOST_PORT

## Notes

- Uploaded files are stored in the local uploads directory.
- The agent can use OpenAI when OPENAI_API_KEY is set.
- The command tool is intended for local demo use.
