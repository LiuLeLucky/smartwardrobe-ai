import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "Explain how a website integrates an AI model into its frontend and backend. Describe the overall architecture, including how user input is captured, sent to a backend server, forwarded to an AI API, and returned to the frontend. Include details on authentication (API keys), request/response handling, streaming responses, error handling, latency considerations, and how to securely manage and protect the API key. Also explain common implementation patterns (e.g., REST API, WebSocket, or serverless functions) and how to design the system for scalability and cost control.",
        }
    ],
)
print(message.content)