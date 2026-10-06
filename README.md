*This project has been created as part of the 42 curriculum by bgix.*


# <span style="font-size: 60px;">RAG</span> <br> <p style="text-align: right; font-size: 30px;">Against the machine</p> 
![Image](./data/assets/42.jpg)

![Version](https://img.shields.io/badge/version-1.0-blue)
![Language](https://img.shields.io/badge/python-0?logo=python&logoColor=white)

# Description

# Intruction

# Resources

# System Architecture

```mermaid
architecture-beta
    group rag(mdi:network-attached-storage)[RAG]
    group main(mdi:code-array)[Main] in rag
    group model(mdi:assistant)[AI] in rag
    group chunkerservice(mdi:collage)[ChunkerService] in rag

    service chunker(mdi:widgets)[Chunker] in chunkerservice
    service bm25(mdi:database-search)[BM25] in chunkerservice
    service index(mdi:database)[indexer] in chunkerservice
    service stored1(mdi:code-json)[Stored as Json] in chunkerservice
    service filter(mdi:radar)["sources"] in rag


    index:B --> T:chunker
    chunker:L --> R:stored1
    stored1:B --> L:bm25
    q:B --> T:process
    service user(mdi:user-arrow-right)["user"] in main
    service q(mdi:chat-question)["question"] in main
    service process(mdi:gear-outline)["process"] in main

    align row index user
    align row stored1 chunker q
    align column index chunker bm25
    align column user q process
    align row bm25 filter process

    align column user q process anwser
    align column user filter ai prompt
    align row ai anwser

    user:B --> T:q

    process:L --> R:filter
    bm25:R --> L:filter
    filter:L --> R:bm25

    service ai(mdi:robot)["LLM"] in model
    service prompt(mdi:comment-text)["Default Prompt"] in model
    service anwser(mdi:message-cog)["Reponse"] in model

    filter:B --> T:ai
    ai:T --> B:filter
    prompt:T --> B:ai
    ai:R --> L:anwser
    anwser:T --> B:process


```

# Chunking Strategy

# Retrieval Method

# Performance Analysis

# Design Decisions

# Challenge Faced

# Exemple Usages