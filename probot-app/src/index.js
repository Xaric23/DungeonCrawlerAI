/**
 * DungeonCrawlerAI Probot App
 * Automates repository workflows and community management
 */

/**
 * @param {import('probot').Probot} app
 */
module.exports = (app) => {
  app.log.info("🏰 DungeonCrawler Bot loaded!");

  // ============ ISSUE AUTOMATION ============

  // Auto-label new issues based on content
  app.on("issues.opened", async (context) => {
    const issue = context.payload.issue;
    const title = issue.title.toLowerCase();
    const body = (issue.body || "").toLowerCase();
    const labels = [];

    // Detect issue type from content using word boundaries
    if (/\bbug\b/.test(title) || /\berror\b/.test(body) || /\bcrash\b/.test(body) || body.includes("not working")) {
      labels.push("bug");
    }
    if (/\bfeature\b/.test(title) || /\brequest\b/.test(title) || body.includes("would be nice") || /\bsuggestion\b/.test(body)) {
      labels.push("enhancement");
    }
    if (/\bdoc\b/.test(title) || /\bdocumentation\b/.test(body) || /\breadme\b/.test(body)) {
      labels.push("documentation");
    }

    // Detect component
    if (body.includes("hero") || body.includes("enemy") || body.includes("dungeon") || body.includes("combat")) {
      labels.push("game-core");
    }
    if (body.includes("ai") || body.includes("behavior") || body.includes("decision")) {
      labels.push("ai");
    }
    if (body.includes("web") || body.includes("dashboard") || body.includes("browser") || body.includes("flask")) {
      labels.push("web");
    }
    if (body.includes("ui") || body.includes("display") || body.includes("visualization")) {
      labels.push("ui");
    }

    // Apply labels if any detected
    if (labels.length > 0) {
      await context.octokit.issues.addLabels(context.issue({ labels }));
      app.log.info(`Labeled issue #${issue.number} with: ${labels.join(", ")}`);
    }

    // Welcome message for first-time contributors
    const creator = issue.user.login;
    const { data: issues } = await context.octokit.issues.listForRepo({
      ...context.repo(),
      creator,
      state: "all",
    });

    if (issues.length === 1) {
      const welcomeMessage = `👋 Welcome to DungeonCrawlerAI, @${creator}!

Thanks for opening your first issue! We appreciate your contribution to the project.

A maintainer will review this soon. In the meantime:
- 📖 Check out our [README](https://github.com/Xaric23/DungeonCrawlerAI/blob/main/README_ENHANCED.md) for feature documentation
- 🎮 Try the [web demo](https://xaric23.github.io/DungeonCrawlerAI/)
- 💬 Feel free to provide any additional details that might help

Happy dungeon crawling! 🏰`;

      await context.octokit.issues.createComment(context.issue({ body: welcomeMessage }));
    }
  });

  // ============ PULL REQUEST AUTOMATION ============

  // Auto-label and welcome PRs
  app.on("pull_request.opened", async (context) => {
    const pr = context.payload.pull_request;
    const title = pr.title.toLowerCase();
    const labels = [];

    // Detect PR type
    if (title.includes("fix") || title.includes("bug")) {
      labels.push("bug");
    }
    if (title.includes("feat") || title.includes("add") || title.includes("new")) {
      labels.push("enhancement");
    }
    if (title.includes("doc") || title.includes("readme")) {
      labels.push("documentation");
    }
    if (title.includes("deps") || title.includes("dependabot") || title.includes("bump")) {
      labels.push("dependencies");
    }
    if (title.includes("ci") || title.includes("workflow") || title.includes("action")) {
      labels.push("github-actions");
    }

    if (labels.length > 0) {
      await context.octokit.issues.addLabels(context.issue({ labels }));
    }

    // Check for first-time contributor
    const creator = pr.user.login;
    const { data: creatorIssues } = await context.octokit.issues.listForRepo({
      ...context.repo(),
      state: "all",
      creator,
    });

    const creatorPRs = creatorIssues.filter((issue) => issue.pull_request);
    if (creatorPRs.length === 1) {
      const welcomeMessage = `🎉 Thanks for your first PR, @${creator}!

We're excited to have you contribute to DungeonCrawlerAI!

**Checklist for review:**
- [ ] Code follows existing style conventions
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if needed)

A maintainer will review this soon. Thanks for helping make the dungeon more dangerous! 😈`;

      await context.octokit.issues.createComment(context.issue({ body: welcomeMessage }));
    }
  });

  // ============ STALE ISSUE MANAGEMENT ============

  /**
   * Note: Stale issue management requires scheduled execution which is not
   * natively supported by Probot's event system.
   * 
   * To implement stale issue management, you have two options:
   * 
   * 1. Use GitHub Actions with a cron schedule:
   *    - Create a workflow that runs on a schedule (e.g., daily)
   *    - Trigger a repository_dispatch event
   *    - Handle the event here with app.on("repository_dispatch")
   * 
   * 2. Use the probot-scheduler plugin:
   *    - Install: npm install probot-scheduler
   *    - Configure in this file to run periodic checks
   * 
   * Example GitHub Actions workflow (.github/workflows/stale-check.yml):
   * 
   * ```yaml
   * name: Check Stale Issues
   * on:
   *   schedule:
   *     - cron: '0 0 * * *'  # Run daily at midnight
   * jobs:
   *   check-stale:
   *     runs-on: ubuntu-latest
   *     steps:
   *       - uses: actions/stale@v8
   *         with:
   *           days-before-stale: 30
   *           days-before-close: 7
   *           stale-issue-label: 'stale'
   *           stale-issue-message: 'This issue has been marked as stale'
   *           close-issue-message: 'This issue has been closed due to inactivity'
   * ```
   */

  // ============ COMMENT REACTIONS ============

  // React to specific keywords in comments
  app.on("issue_comment.created", async (context) => {
    const comment = context.payload.comment;
    const body = comment.body.toLowerCase();

    // Thank contributors
    if (body.includes("thank") || body.includes("thanks") || body.includes("awesome")) {
      await context.octokit.reactions.createForIssueComment({
        ...context.repo(),
        comment_id: comment.id,
        content: "heart",
      });
    }

    // Celebrate fixes
    if (body.includes("fixed") || body.includes("resolved") || body.includes("solved")) {
      await context.octokit.reactions.createForIssueComment({
        ...context.repo(),
        comment_id: comment.id,
        content: "hooray",
      });
    }
  });

  // ============ RELEASE NOTES ============

  // Auto-generate release notes on tag push
  app.on("release.published", async (context) => {
    const release = context.payload.release;

    // Add game-specific notes
    const additionalNotes = `

---

## 🎮 Play Now!

- **Web Version:** https://xaric23.github.io/DungeonCrawlerAI/
- **Download EXE:** Check the assets below

## 🚀 Quick Start

\`\`\`bash
# Clone and run
git clone https://github.com/Xaric23/DungeonCrawlerAI.git
cd DungeonCrawlerAI
python main_enhanced.py
\`\`\`

Happy dungeon crawling! 🏰`;

    // Sanitize and update release body
    const existingBody = release.body || "";
    await context.octokit.repos.updateRelease({
      ...context.repo(),
      release_id: release.id,
      body: existingBody + additionalNotes,
    });
  });
};
