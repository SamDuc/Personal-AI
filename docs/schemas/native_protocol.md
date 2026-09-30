# Native Protocol Contract

## 1. Purpose

This contract defines the native wire-protocol boundary used by the
Personal AI provider adapter.

The current implementation uses an OpenAI-compatible HTTP chat-completions
protocol behind the provider boundary.

The native protocol is an implementation detail of the provider adapter.
Higher-level LLM runtime, integration, agent, and router layers MUST NOT
depend on this wire protocol.

## 2. Boundary

The protocol boundary is:

`LLMProvider -> OpenAICompatibleProvider -> HTTP wire protocol`

The following layers MUST remain protocol-independent:

- `LLMRuntime`
- `LLMIntegration`
- `Agent`
- `AgentRouter`
- application bootstrap

## 3. Request

The provider adapter MUST translate an `LLMRequest` into an HTTP POST
request.

The request endpoint is:

`{base_url}/chat/completions`

The request body MUST be JSON containing:

- `model`
- `messages`

Each message MUST contain:

- `role`
- `content`

The order of messages MUST be preserved.

## 4. HTTP

The native protocol request MUST:

- use HTTP POST;
- use `Content-Type: application/json`;
- serialize the request body as UTF-8 JSON;
- apply the configured request timeout.

The adapter MUST NOT expose HTTP construction to higher-level layers.

## 5. Authentication

When `api_key_env` is configured:

- the API key MUST be read from the environment at request time;
- the API key MUST be sent through the `Authorization` header using
  `Bearer <token>`;
- the provider object MUST NOT persist the API key value;
- missing credentials MUST fail explicitly.

The API key value MUST NOT appear in error messages or diagnostic state.

## 6. Response

A successful native response MUST contain:

`choices[0].message.content`

The extracted content MUST be text.

The adapter MUST return that content through the stable `LLMResponse`
interface.

The adapter MUST preserve response text exactly and MUST NOT normalize,
trim, rewrite, or otherwise transform the generated text.

## 7. Invalid Responses

Malformed JSON MUST fail explicitly.

A response missing the required response structure MUST fail explicitly.

Non-text response content MUST fail explicitly.

The adapter MUST NOT fabricate an `LLMResponse`.

## 8. HTTP Failures

HTTP failures MUST remain observable through an explicit runtime error.

The HTTP status code MUST remain observable in the adapter-generated error
for HTTP failures.

The adapter MUST NOT silently convert an HTTP failure into a successful
response.

## 9. Transport Failures

Network/URL transport failures MUST fail explicitly.

The adapter MUST NOT fabricate a successful response after a transport
failure.

## 10. Recovery Scope

This contract does not define:

- retries;
- exponential backoff;
- provider fallback;
- automatic provider switching;
- circuit breakers;
- health checks;
- cross-provider orchestration.

Those mechanisms are outside the native protocol contract.

## 11. Secret Boundary

Protocol implementation MUST NOT:

- store raw API-key values;
- expose raw API-key values through object representation;
- include raw API-key values in errors;
- move credentials into higher-level runtime objects.

## 12. Provider Independence

The stable `LLMProvider` interface remains provider-independent.

The native protocol MUST remain isolated inside the provider adapter.

Adding another protocol MUST NOT require changes to:

- `LLMRuntime`;
- `LLMIntegration`;
- `Agent`;
- `AgentRouter`.

## 13. Contract Version

Contract version: 1.
