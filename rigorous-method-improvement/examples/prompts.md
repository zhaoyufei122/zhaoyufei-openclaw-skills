# Example prompts

Useful for checking that the skill triggers when it should and stays quiet when it should not.

## Should trigger

- "这篇论文的方法和代码都在仓库里，帮我按严格科研流程找能打过 baseline 的改进，并写到能投稿的程度。"
- "Here's the repo for the ICML paper on incremental BPE tokenization and their benchmark script. Can we beat their numbers with something that's actually a new idea, not just tuning? Write it up like a paper."
- "ok so my advisor wants me to extend X-Maha (the OOD detection method, code in ./x_maha) on the CIFAR-100 SCOOD benchmark. find where it's weak and try a few ideas, I have one GPU for the afternoon"
- "I added a gating module to the time-series forecaster in this repo and MSE dropped 4%. Before I get excited: is this gain real? Do the ablations and check I didn't leak anything."
- "Take the TabSwift baseline, find 2-3 mechanistic improvements, run them properly with seeds, and give me a report with tables I could put in a workshop submission."
- "This is my own method from last year. Run it through a proper review-and-rebuttal cycle and tell me what a NeurIPS reviewer would attack, then run the experiments that would answer them."

## Should not trigger

- "Explain how Mahalanobis-distance OOD detection works." (explanation, no experiment)
- "Summarise this paper for me." (reading, not improving)
- "Tune the learning rate and batch size for this training script to get the best accuracy." (configuration tuning; the skill's 'What counts' section explicitly excludes this as a contribution)
- "Write the related-work section for my paper on OOD detection." (writing only)
- "Fix the failing tests in the evaluation harness." (engineering on the evaluator, which the skill treats as off-limits during an improvement run)
