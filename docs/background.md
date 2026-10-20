# Project background

Well, to summarize: I did this in order to get **agentic LLMs capable of designing buildable, physical things!**

Finding **LDraw**, an **assembly language** (pun intended! 😜) that would be at the same time **simple**, **low level**, and **executable** in order to **produce 3D CAD models**, gave me the idea of **experimenting** with both **ChatGPT** and **Claude** in order to try and make them **code in LDraw**, same as they do with other programming languages.

To my surprise, even though this language is heavily focused on **math** (parts rotations, positioning...), which LLMs are **usually bad** at, **agents did pretty well** instead on initial tests, and subsequent projects also yielded **good results**, but **never enough** in order to consider generated models to be correct:

- **Initial research:** [ldbuilder-ai](https://github.com/anteloc/ldbuilder-ai)
- **1st attempt** at an agentic python tooling: [py2bricks](https://github.com/anteloc/py2bricks)
- **2nd attempt**: [py4bricks](https://github.com/anteloc/py4bricks)

These three attempts, and quite some other experimentation, led me to the following **conclusions**:

**💡 Conclusion 1:** there is a **minimum resistance path to geometry math** for agents, i.e.:

- **Giving the agents tooling** to generate LDraw sources would **sidestep (evil!) geometry math**
- ... because they do way **better** at generating **python code** that **produces math**
- ... **than on producing math themselves!**

**💡 Conclusion 2:** 

- Agents tend to do **better when learning** from python **code** that **produces models**
- ... than from **models themselves** (LDraw's evil geometry, again...)

Then, the **only thing left 🤔** was to create a python-based tooling with the required **primitives, verbs, constructive vocabulary**... so agents would **learn by example** and **do similar things on their own.**

Which proved to be really **hard to get right**, even if vibe coding it... until **GPT-6 Astra** and **Claude Opus 5.5** arrived... and **vibe-coded it right!** 🚀🚀🚀

