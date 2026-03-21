
---
title: Understanding the Core Building Blocks
tags: [concepts, fundamentals, llm]
---

In this chapter we will learn about what ingredients we might be needing — like before cooking, we need some things. We don't throw random stuff together and hope for something good to happen.

There are some concepts that you need to understand before building an AI agent, but don't worry — there's only a few of them. 

#### How does the llm works?

You dont need to understand how it works the neurel networks or anything expensive learning r algoritmic thinking , What you need to understand that LLM takes the text anlysis the query and answer based on user query 

Think of its like a software that takes will takes our log file analyzes that log and recognizes that pattern that learned it during its training and generates the text based on what makes sense.

You have 2 options that you might be using to make your llm application:

1. Cloud APIs: This are the services that host models for you and send your data over the internet and they send back the results. This is th eeasiet and most commonly method that people use worldwide 
2. Self hosted LLM: These are the local models that you nee to configure yourself and this keeps your data rivate if your biggest concern is about privacy this can make your data in your hands and make things easier for the organization privacy 

### How Does Our LLM Get the Logs?

Any AI model can't access your data directly — that's why we use [[../03 - Implementation/Data Retrieval|Data Retrieval]].