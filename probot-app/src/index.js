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

    // Detect issue type from content
    if (title.includes("bug") || body.includes("error") || body.includes("crash") || body.includes("not working")) {
      labels.push("bug");
    }
    if (title.includes("feature") || title.includes("request") || body.includes("would be nice") || body.includes("suggestion")) {
      labels.push("enhancement");
    }
    if (title.includes("doc") || body.includes("documentation") || body.includes("readme")) {
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
- 📖 Check out our [README](../blob/main/README_ENHANCED.md) for feature documentation
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
    const { data: prs } = await context.octokit.pulls.list({
      ...context.repo(),
      state: "all",
    });

    const creatorPRs = prs.filter((p) => p.user.login === creator);
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

  // Mark stale issues (run via scheduled workflow)
  app.on("schedule.repository", async (context) => {
    const daysUntilStale = 30;
    const daysUntilClose = 7;
    const staleLabel = "stale";

    const { data: issues } = await context.octokit.issues.listForRepo({
      ...context.repo(),
      state: "open",
      per_page: 100,
    });

    const now = new Date();

    for (const issue of issues) {
      const updatedAt = new Date(issue.updated_at);
      const daysSinceUpdate = (now - updatedAt) / (1000 * 60 * 60 * 24);

      const isStale = issue.labels.some((l) => l.name === staleLabel);

      if (daysSinceUpdate > daysUntilStale && !isStale) {
        // Mark as stale
        await context.octokit.issues.addLabels({
          ...context.repo(),
          issue_number: issue.number,
          labels: [staleLabel],
        });

        await context.octokit.issues.createComment({
          ...context.repo(),
          issue_number: issue.number,
          body: `⏰ This issue has been automatically marked as stale because it has not had activity in ${daysUntilStale} days.

It will be closed in ${daysUntilClose} days if no further activity occurs. If this issue is still relevant, please comment or update it.`,
        });
      } else if (isStale && daysSinceUpdate > daysUntilStale + daysUntilClose) {
        // Close stale issue
        await context.octokit.issues.update({
          ...context.repo(),
          issue_number: issue.number,
          state: "closed",
        });

        await context.octokit.issues.createComment({
          ...context.repo(),
          issue_number: issue.number,
          body: "🔒 This issue has been closed due to inactivity. Feel free to reopen if it's still relevant!",
        });
      }
    }
  });

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

    // Update release body
    await context.octokit.repos.updateRelease({
      ...context.repo(),
      release_id: release.id,
      body: release.body + additionalNotes,
    });
  });
};
