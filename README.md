# Ringi-AI

AI-powered Japanese decision making system “Ringi (稟議)”

## Background

Decision-making among Japanese people is characterized by a collective approach, and this is no exception within enterprises. While this approach helps taking firm steps that minimize risk, it can be a serious drawback, potentially causing companies to stagnate in a rapidly changing environment. This project proposes automating the Japanese enterprise decision-making process (“Ringi”) by an AI reviewer, which could significantly accelerate progress and help Japanese enterprises to stay competitive in global industries.

The current process can minimize risks but has significant drawbacks. I consider the major problems of the current decision-making system are followings:

1. **The process makes decision-making slower.** It becomes very difficult for the company to keep up with a fast-changing environment.
2. **The process discourages employees from taking initiative.** The extensive approvals make employees overly cautious and could discourage them from starting something new.
3. **Significant resources are wasted on reviews.** Reviewing departments consume substantial resources, and worse, large volumes of minor and less critical applications drain employees' time and attention, preventing them from focusing on important applications.

## Ringi system by AI-reviewers

The current project proposes a Ringi system with AI reviewers. First, AI reviewers are assigned to each department, working in parallel to review applications. The reviewing process in each department can be broken down into the following steps, which can be accelerated by AI reviewers:

1. **Assessment**: The AI reviews the application, gathers necessary information, and determines whether it complies with company policies. Each department prepares review criteria in advance, and the AI makes decisions based on these criteria.
2. **Suggestion**: The AI provides recommendations to mitigate risks or enhance the benefits of the application. Each department prepares a knowledge base from previous applications, enabling the AI to offer suggestions based on past cases.

By implementing this process, the time required for reviews can be significantly reduced, leading to faster decision-making for Japanese companies.

## Prototype example: AI-Reviewer of IT department

I created a prototype of an AI reviewer for the IT department. (where I work) This prototype is built upon the original work of an AI scientist [1]. I designed a hypothetical application format and review criteria. I didn’t implement the knowledge base for this prototype.

- Please refer to **run_ai_reviews.ipynb** to run the code.
- You need to set OPENAI_API_KEY in .env file to run the agent.

## References

[1] AI Scientist:
https://arxiv.org/abs/2408.06292,
https://github.com/SakanaAI/AI-Scientist
