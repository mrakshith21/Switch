# AI IDE

Tasks

1. Index code in a directory
    - Embedding model
    - Chunking strategy
    - Storage, update and retrieval of chunks

2. Agentic code editing
    - Tools like read file, edit file, grep, etc.
    - Step by step reasoning

3. Models
    - Popular LLMs like GPT, Gemini, .. for agentic decisions as well as code writing
    - Smaller models for applying code edits





Agent Graph


User Prompt 

    |
    v

1. Understands what to do
    - Context fetching
    - Prompt, Query for info in codebase, grep, ...

2. Plans action
    - Create a TODO list

3. for each item in list
    - identify blocks of code (or files) which require changes or creation
    - Prompt LLM and get replacement code
    - Pass through linter 
        -> If successful, apply the change
        -> If failed, get reason and reprompt LLM.

[Optional]
4. Validate the changes with a test or build, etc.
