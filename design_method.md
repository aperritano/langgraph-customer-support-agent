

Method: Keep it Simple

This a demotration of using the langchain ecosystem to develop a system customer service agent. Part of this is learning about all the different aspect of that ecoystem and the many ways agents can be developed. The agent presented is a simple agent that uses tools and to look up customer data. The data store is a vector database for polices, and mock customer data. 

Image of agent graph. 

The customer is able to communicate with the agent about orders, refunds, etc... If the issue is escalatie it interrrupts to create a ticket for a human interject. 

The project also has TDD tests, langsmith evals and datasets, and dockerfile configuration. It was tested using Ollama with the LLM "llama3.1:latest". It uses the langchain studio also and the agent ui for a simple streaming chat interface. 


A complete evaluation framework for the customer support agent that automatically tests responses against 10 diverse customer scenarios and scores them using 5 automated evaluators. The system creates a dataset, runs the agent against each test case, evaluates responses for tool usage, keyword presence, response quality, empathy, and actionability, then uploads detailed results with full conversation traces to the LangSmith dashboard at <https://smith.langchain.com>. Results include aggregate scores, per-test feedback explaining why tests passed or failed, and complete execution traces for debugging. Run with python -m src.support_agent.tests.eval_langsmith to execute evaluations, then view detailed metrics and trends in the LangSmith web interface to track improvements over time and catch regressions.

Next Steps

- Executing actual workflows for business processes like refunds, etc...even to the degree that there is an agent for every workflow. supervisor design pattern from our Multi-agent examples. a "primary assistant" to route between these


- more sofificated Interprut confirmations and executions
- SQL based customer data